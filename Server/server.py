from aiogram import Bot, Dispatcher, types, executor
import logging
from Server.middleware import Middleware
from BotApp.Instruments import BinanceFutures
import os
import config
API_TOKEN = os.getenv('API_TOKEN')
new_ticker_mode = 0
trade_access = 0
lev = 1
max_pos = 4
logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(Middleware(config.user_id))


@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Старт', callback_data='start_trade_btn'))
    keyboard.add(types.InlineKeyboardButton('Настройки', callback_data='settings_btn'))
    await message.answer('Добро пожаловать', reply_markup=keyboard)
    await message.delete()


# Дублирование главного меню, вызывающееся уже с кнопок
@dp.callback_query_handler(lambda c: c.data == 'welcome_btn')
async def main_menu(callback_query: types.CallbackQuery):
    global trade_access
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Старт', callback_data='start_trade_btn'))
    keyboard.add(types.InlineKeyboardButton('Настройки', callback_data='settings_btn'))
    await callback_query.message.answer('Добро пожаловать', reply_markup=keyboard)
    await callback_query.message.delete()
    trade_access = 0


# Начинаем торговлю, после нажатия этой кнопки, бот начинает искать позиции
@dp.callback_query_handler(lambda c: c.data == 'start_trade_btn')
async def trading(callback_query: types.CallbackQuery):
    global trade_access
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Показать открытые позиции', callback_data='opened_btn'))
    keyboard.add(types.InlineKeyboardButton('Остановить торговлю', callback_data='welcome_btn'))
    await bot.send_message(user_id, f'Торгую на {lev} плече\n'
                                    f'Максимальное количество позиций: {max_pos}', reply_markup=keyboard)
    await callback_query.message.delete()
    trade_access = 1


@dp.callback_query_handler(lambda c: c.data == 'opened_btn')
async def opened_binance_fut(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    for i in BinanceFutures.coins:
        if i.pos != 0:
            keyboard.add(types.InlineKeyboardButton(str(i.name), callback_data='pos_' + i.name, ))
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='start_trade_btn'))
    await bot.send_message(user_id, 'Открытые ботом позиции:', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('pos_'))
async def position_info(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Закрыть позицию', callback_data=f'exit_pos_{callback_query.data[3:]}'))
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='start_trade_btn'))
    for i in BinanceFutures.coins:
        if i.name == callback_query.data[3:]:
            await bot.send_message(user_id, f'Позиция по {i.name}, если закроем прямо сейчас, '
                                            f'то заработаем: {await i.get_position_info()} USDT',
                                   reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('exit_pos_'))
async def exit_position(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='start_trade_btn'))
    for i in BinanceFutures.coins:
        if i.name == callback_query.data[8:]:
            await bot.send_message(user_id, f'Позиция по {i.name} закрыта',
                                   reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'settings_btn')
async def settings_binance_fut(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Макс. кол-во позиций', callback_data='max_btn', ))
    keyboard.add(types.InlineKeyboardButton('Плечо', callback_data='lev_btn', ))
    keyboard.add(types.InlineKeyboardButton('Настройка тикеров', callback_data='ticker_btn', ))
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='welcome_btn'))
    await bot.send_message(user_id, 'Что настраиваем?', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'max_btn')
async def settings_max(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('1', callback_data='max_btn_1', ),
                 types.InlineKeyboardButton('2', callback_data='max_btn_2', ),
                 types.InlineKeyboardButton('4', callback_data='max_btn_4', ),
                 )
    keyboard.add(types.InlineKeyboardButton('6', callback_data='max_btn_6', ),
                 types.InlineKeyboardButton('8', callback_data='max_btn_8', ),
                 types.InlineKeyboardButton('Назад', callback_data='settings_btn'),
                 )
    await bot.send_message(user_id, 'Выбери максимальное количество позиций, которые бот может держать.\nТвой депозит '
                                    'поделится на количество позиций на равные части, и бот будет заходить не больше '
                                    'этой суммы', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('max_btn_'))
async def settings_change_max(callback_query: types.CallbackQuery):
    global max_pos
    max_pos = callback_query.data[8]
    # change_max_pos()
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='settings_btn', ))
    await bot.send_message(user_id, f'Макс количество позиций: {max_pos}', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'lev_btn')
async def settings_max(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('1', callback_data='lev_btn_1', ),
                 types.InlineKeyboardButton('2', callback_data='lev_btn_2', ),
                 types.InlineKeyboardButton('5', callback_data='lev_btn_5', ),
                 )
    keyboard.add(types.InlineKeyboardButton('10', callback_data='lev_btn_10', ),
                 types.InlineKeyboardButton('20', callback_data='lev_btn_20', ),
                 types.InlineKeyboardButton('Назад', callback_data='settings_btn'),
                 )
    await bot.send_message(user_id, 'Выбери максимальное количество позиций, которые бот может держать.\nТвой депозит '
                                    'поделится на количество позиций на равные части, и бот будет заходить не больше '
                                    'этой суммы', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('lev_btn_'))
async def settings_change_max(callback_query: types.CallbackQuery):
    global lev
    lev = callback_query.data[8:]
    await BinanceFutures.change_leverage(lev)
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='settings_btn', ))
    await bot.send_message(user_id, f'Установлено плечо: {lev}', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'ticker_btn')
async def settings_ticker(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Посмотреть настроенные тикеры', callback_data='ticker_list', ),)
    keyboard.add(types.InlineKeyboardButton('Добавить новый тикер', callback_data='new_ticker', ),)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='settings_btn', ),)
    await bot.send_message(user_id, 'Что делаем?', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'ticker_list')
async def settings_ticker_list(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    for i in BinanceFutures.coins:
        print(i)
        keyboard.add(types.InlineKeyboardButton(i.name, callback_data=f'ticker_list_{i.name}',),)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='ticker_btn', ), )
    await bot.send_message(user_id, 'Сейчас я использую эти тикеры:', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('ticker_list_'))
async def settings_ticker_info(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Удалить тикер', callback_data=f'delete_{callback_query.data[12:]}', ), )
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='ticker_list', ), )
    await bot.send_message(user_id, f'Тикер {callback_query.data[12:]}', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith('delete_'))
async def deleting_ticker(callback_query: types.CallbackQuery):
    from BotApp.InstrumentConstructors import BinanceFuturesConstructor
    BinanceFuturesConstructor.deconstruct(callback_query.data[7:])
    keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Назад', callback_data='ticker_list', ), )
    await bot.send_message(user_id, f'Тикер {callback_query.data[7:]} удалён', reply_markup=keyboard)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'new_ticker')
async def new_ticker(callback_query: types.CallbackQuery):
    global new_ticker_mode
    new_ticker_mode = 1
    await bot.send_message(user_id, 'Введите тикер')
    await callback_query.message.delete()


@dp.message_handler()
async def new_ticker_handler(message: types.Message):
    global new_ticker_mode
    if new_ticker_mode == 1:
        from BotApp.InstrumentConstructors import BinanceFuturesConstructor
        await BinanceFuturesConstructor.construct(message.text)
        new_ticker_mode = 0


async def new_ticker_added():
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Назад', callback_data='ticker_list', ), )
    await bot.send_message(user_id, 'Ваш тикер добавлен', reply_markup=keyboard)


async def new_ticker_exception():
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Назад', callback_data='ticker_list', ), )
    await bot.send_message(user_id, 'Не удаётся добавить ваш тикер в систему', reply_markup=keyboard)


async def enter_long_message(name, price):
    await bot.send_message(user_id, f'Вход в лонг по {name}\nЦена: {price}')


async def enter_short_message(name, price):
    await bot.send_message(user_id, f'Вход в шорт по {name}\n'
                                    f'Цена: {price}')


async def exit_message(name, income):
    await bot.send_message(user_id, f'Выход из {name}\n'
                                    f'Прибыль: {income}')


async def cancel_order(name, income):
    await bot.send_message(user_id, f'К сожалению, ордер по {name} так и не сработал, пришлось его отменить.\n'
                                    f'Могли бы заработать: {income}')


async def user_intervention(name, income):
    await bot.send_message(user_id, f"Не удалось закрыть и позицию и ордер по {name}, обычно это происходит из-за "
                                    f"вмешательства пользователя в торговлю\nМогли бы заработать: {income}")


async def run_bot():
    executor.start_polling(dp, skip_updates=True)
