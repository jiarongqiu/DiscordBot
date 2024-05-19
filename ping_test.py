import aiohttp
import asyncio

async def test_connection():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://discord.com/api/v9') as response:
                print('Connected to Discord API:', response.status)
        except aiohttp.ClientConnectorError as e:
            print('Connection error:', e)
print('Done.')
asyncio.run(test_connection())
