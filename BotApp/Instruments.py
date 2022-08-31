import asyncio
from BotApp.TA_Indicators import TAIndicators
from BotApp.AbsractMethods import Instrument
from BotApp.connection import binance_connector
from binance.enums import *
from binance.exceptions import BinanceAPIException
import math
import logging


# Класс, содержащий всю логику управления бинансом
class BinanceFutures(Instrument, TAIndicators):
    income = 0
    max_pos = 4
    openedpos = 0
    coins = []
    lev = 1
    commision = 0.0006
    balance = 0

    def __init__(self, name, time_frame):
        super().__init__()
        self.precision = None
        self.amount = None
        self.name = name
        self.time_frame = time_frame
        self.klines = []
        self.max = []
        self.min = []
        self.close = []
        self.ema = []
        self.pos = 0
        self.enterpoint = None
        self.order = None
        BinanceFutures.coins.append(self)

    @classmethod
    @binance_connector
    async def check_balance(cls, client):
        a = await client.futures_account_balance()
        BinanceFutures.balance = float(a[-4]['withdrawAvailable'])
        return BinanceFutures.balance

    @binance_connector
    async def get_precision(self, client):
        info = await client.futures_exchange_info()
        for x in info['symbols']:
            if x['symbol'] == self.name:
                self.precision = int(x['quantityPrecision'])
                return self.precision

    # Получение инфы о инструменте, далее эту инфу уже передаём в индикаторы
    @binance_connector
    async def analysis(self, client):
        # [0:Open time, 1:Open, 2:High, 3:Low, 4:Close, 5:Volume, 6:lose time, 7:Quote asset volume
        # 8:Number of trades, 9:Taker buy base asset volume, 10:Taker buy quote asset volume, 11:Ignore]
        print(self.name)
        self.klines = await client.futures_klines(symbol=self.name, interval=self.time_frame, limit=1000)
        for i in self.klines:
            self.max.append(float(i[2]))
            self.min.append(float(i[3]))
            self.close.append(float(i[4]))

    @binance_connector
    async def enter_long(self, client):
        from Server import server
        self.pos = 1
        await server.enter_long_message(str(self.name), str(self.close[-1]))
        value = (BinanceFutures.balance / (BinanceFutures.max_pos - BinanceFutures.openedpos)
                 ) * BinanceFutures.lev
        await self.get_precision()
        self.amount = math.floor((value / self.close[-1]) * (10 ** self.precision)) / (10 ** self.precision)
        self.enterpoint = self.close[-1]
        self.order = await client.futures_create_order(
            symbol=self.name,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            price=self.close[-1],
            quantity=self.amount
        )
        BinanceFutures.openedpos += 1

    @binance_connector
    async def enter_short(self, client):
        from Server import server
        self.pos = -1
        await server.enter_short_message(str(self.name), str(self.close[-1]))
        value = (BinanceFutures.balance / (BinanceFutures.max_pos - BinanceFutures.openedpos)
                 ) * BinanceFutures.lev
        await self.get_precision()
        self.amount = math.floor((value / self.close[-1]) * (10 ** self.precision)) / (10 ** self.precision)
        self.enterpoint = self.close[-1]
        self.order = await client.futures_create_order(
            symbol=self.name,
            side=SIDE_SELL,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            price=self.close[-1],
            quantity=self.amount)
        BinanceFutures.openedpos += 1

    @binance_connector
    async def exit_long(self, client):
        from Server import server
        self.pos = 0
        BinanceFutures.openedpos -= 1
        income_now = ((self.close[-1] * self.amount) - (self.enterpoint * self.amount)
                      ) * (1 - (BinanceFutures.commision * BinanceFutures.lev))
        try:
            await client.futures_create_order(
                symbol=self.name,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                reduceOnly=True,
                quantity=self.amount)
            BinanceFutures.income += income_now
            await server.exit_message(self.name, income_now)
        except BinanceAPIException:
            try:
                await client.futures_cancel_order(symbol=self.name, orderid=self.order['orderId'])
                await server.cancel_order(self.name, income_now)
            except BinanceAPIException as err:
                BinanceFutures.income += income_now
                await server.user_intervention(self.name, income_now)
                logging.error(err, exc_info=True)

    @binance_connector
    async def exit_short(self, client):
        from Server import server
        self.pos = 0
        BinanceFutures.openedpos -= 1
        income_now = ((self.enterpoint * self.amount) - (self.close[-1] * self.amount)
                      ) * (1 - (BinanceFutures.commision * BinanceFutures.lev))
        try:
            await client.futures_create_order(
                symbol=self.name,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                reduceOnly=True,
                quantity=self.amount)
            BinanceFutures.income += income_now
            await server.exit_message(self.name, income_now)
        except BinanceAPIException:
            try:
                await client.futures_cancel_order(symbol=self.name, orderid=self.order['orderId'])
                await server.cancel_order(self.name, income_now)
            except BinanceAPIException as err:
                BinanceFutures.income += income_now
                await server.user_intervention(self.name, income_now)
                logging.error(err, exc_info=True)

    @classmethod
    @binance_connector
    async def change_leverage(cls, lev, client):
        tasks = []
        for i in BinanceFutures.coins:
            task = asyncio.create_task(client.futures_change_leverage(symbol=i.name, leverage=lev))
            tasks.append(task)
            await asyncio.sleep(0)
        await asyncio.gather(*tasks)

    # Получение инфы о прибыли/убытке с позиции из телеграм-бота
    @binance_connector
    async def get_position_info(self):
        if self.pos > 0:
            income_now = ((self.close * self.amount) - (self.enterpoint * self.amount)
                          ) * (1 - (BinanceFutures.commision * BinanceFutures.lev))
            return income_now
        if self.pos < 0:
            income_now = ((self.enterpoint * self.amount) - (self.close * self.amount)
                          ) * (1 - (BinanceFutures.commision * BinanceFutures.lev))
            return income_now
        else:
            pass
