import asyncio
import logging
import config
import time
from BotApp.Instruments import BinanceFutures
from BotApp.strategy import SampleStrategy
from Server import server
from aiogram import executor
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Полуение количества секунд между свечами
async def get_timer():
    a = 0
    b = 0
    for i in config.time_frame:
        if i.isdigit():
            a += 1
    if config.time_frame[-1] == 's':
        b = 1
    if config.time_frame[-1] == 'm':
        b = 60
    if config.time_frame[-1] == 'h':
        b = 3600
    if config.time_frame[-1] == 'd':
        b = 86400
    timer = int(config.time_frame[0:a]) * b
    return timer


async def main():
    starttime = time.time()
    timer = await get_timer()
    SampleStrategy('BTCUSDT', config.time_frame)
    SampleStrategy('ETHUSDT', config.time_frame)
    while True:
        if server.trade_access:
            tasks = []
            await BinanceFutures.check_balance()
            print(BinanceFutures.balance)
            for i in BinanceFutures.coins:
                task = asyncio.create_task(i.trading())
                tasks.append(task)
                await asyncio.sleep(0)
            await asyncio.gather(*tasks)
            await asyncio.sleep(timer - ((time.time() - starttime) % timer))
        else:
            await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        executor.start_polling(server.dp, skip_updates=True)
    except Exception as err:
        logging.error(err, exc_info=True)
