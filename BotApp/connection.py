import functools
import os
from binance.client import AsyncClient
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')


# Декоратор, подключающий к бинансу, возвращающий client
def binance_connector(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        client = await AsyncClient.create(api_key, api_secret)
        try:
            await func(*args, **kwargs, client=client)
        finally:
            await client.close_connection()
    return wrapper

