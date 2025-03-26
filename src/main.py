import asyncio
import itertools
import json
import logging
import sys

from httpx import AsyncClient, HTTPStatusError

from .constants import AGENTS, MAPS, SIDES, DIFFICULTIES


async def fetch_and_save_data(client: AsyncClient, agent: str, map_name: str, side: str, difficulty: str) -> None:
    try:
        response = await client.get(
            f'https://data.iesdev.com/api/valorant/tips.json?side={side}&difficulty={difficulty}&map={map_name}&agent={agent}&page=1&limit=3000'
        )
        response.raise_for_status()

        data = response.json()

        new_data = {
            'totals': data['totals'],
            'data': [
                {
                    'map': item['map'],
                    'side': item['side'],
                    'agent': item['agent'],
                    'title': item['title'],
                    'video': item['video'],
                    'difficulty': item['difficulty'],
                    'description': item['description']
                }
                for item in data['list']
            ]
        }

        output_file = f'src/lineups/{agent}/{map_name}/{side}/{difficulty}/data.json'

        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(new_data, file, indent=4, ensure_ascii=False)

        logging.info(
            f'Data successfully written to: {agent}/{map_name}/{side}/{difficulty} <---> Count: {data['totals']}'
        )
    except Exception as e:
        if isinstance(e, HTTPStatusError):
            logging.error(f'HTTP error {e.response.status_code} for {agent}/{map_name}/{side}/{difficulty}')
        else:
            logging.error(f'Unexpected error processing {agent}/{map_name}/{side}/{difficulty}: {e}')


async def main() -> None:
    client = AsyncClient()

    for agent, map_name, side, difficulty in itertools.product(AGENTS, MAPS, SIDES, DIFFICULTIES):
        await fetch_and_save_data(client, agent, map_name, side, difficulty)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):

        logging.error('Stopped!')
