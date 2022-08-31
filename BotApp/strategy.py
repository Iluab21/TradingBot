from BotApp.Instruments import BinanceFutures


'''Простая стратения, для понимания что и как работает
    Торговать по ней я не советую, выстраивайте свою стратегию
    Для того чтобы протестировать свою стратегию рекомендую использовать бектестирование на TradingView'''


class SampleStrategy(BinanceFutures):
    def macd_long_signal(self):
        [macd, signal] = self.indicator_macd(26, 16, 9)
        if signal[-1] < 0:
            if macd[-1] > signal[-1]:
                return True
        else:
            return False

    def macd_short_signal(self):
        [macd, signal] = self.indicator_macd(26, 16, 9)
        if signal[-1] > 0:
            if macd[-1] < signal[-1]:
                return True
        else:
            return False

    def exit_long_condition(self):
        [macd, signal] = self.indicator_macd(26, 16, 9)
        if macd[-1] < signal[-1]:
            return True
        else:
            return False

    def exit_short_condition(self):
        [macd, signal] = self.indicator_macd(26, 16, 9)
        if macd[-1] > signal[-1]:
            return True
        else:
            return False

    async def trading(self):
        await self.analysis()
        if self.pos == 0:
            if self.macd_long_signal():
                await self.enter_long()
            if self.macd_short_signal():
                await self.enter_short()
        if self.pos == 1:
            if self.exit_long_condition():
                await self.exit_short()
        if self.pos == -1:
            if self.exit_short_condition():
                await self.exit_short()
