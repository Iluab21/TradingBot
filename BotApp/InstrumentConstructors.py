import logging

from BotApp.AbsractMethods import InstumentContructor
from BotApp.Instruments import BinanceFutures
from binance.exceptions import BinanceAPIException
from BotApp.connection import binance_connector
from Server.server import new_ticker_added, new_ticker_exception
import config


# Класс создания удаления монет
class BinanceFuturesConstructor(InstumentContructor):
    @staticmethod
    @binance_connector
    async def construct(name, client):
        try:
            await client.futures_klines(symbol=name, interval=config.time_frame, limit=1)
            BinanceFutures(name=name, time_frame=config.time_frame)
            await new_ticker_added()
        except BinanceAPIException:
            await new_ticker_exception()

    @staticmethod
    def deconstruct(name):
        try:
            for i in BinanceFutures.coins:
                if i.name == name:
                    BinanceFutures.coins.remove(i)
                    break
        except ValueError as err:
            logging.error(err, exc_info=True)
