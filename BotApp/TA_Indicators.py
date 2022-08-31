class TAIndicators:
    def __init__(self):
        self.rma = None
        self.adx = None
        self.minus_di = None
        self.plus_di = None
        self.min = None
        self.max = None
        self.signal = None
        self.macd = None
        self.klines = []
        self.close = []
        self.ema = []
        self.supertrend = []

    def indicator_ema(self, source, period):
        self.ema = []
        past_ema = source[0]
        for i in source:
            alpha = 2 / (period + 1)
            ema = (alpha * i) + ((1 - alpha) * past_ema)
            past_ema = ema
            self.ema.append(ema)
        return self.ema

    def indicator_rma(self, source, period):
        self.rma = []
        past_rma = source[0]
        for i in source:
            alpha = 1 / period
            rma = (alpha * i) + ((1 - alpha) * past_rma)
            past_rma = rma
            self.rma.append(rma)
        return self.rma

    def indicator_supertrend(self, period=10, factor=3):
        close_past = self.close[-1]
        green_line_past = self.close[-1]
        red_line_past = self.close[-1]
        atr_now_list = []
        trend = 0
        for i in self.klines:
            max_now = float(i[2])
            min_now = float(i[3])
            close_now = float(i[4])
            atr_now = max(max_now - min_now,
                          abs(max_now - close_past),
                          abs(min_now - close_past))
            if len(atr_now_list) < period:
                atr_now_list.append(atr_now)
            else:
                atr_now_list.pop(0)
                atr_now_list.append(atr_now)
            atr = (sum(atr_now_list) / period) * factor
            up = (max_now + min_now) / 2 + atr
            dn = (max_now + min_now) / 2 - atr
            if close_past > green_line_past:
                green_line = max(dn, green_line_past)
            else:
                green_line = dn
            if close_past < red_line_past:
                red_line = min(up, red_line_past)
            else:
                red_line = up
            if close_now > red_line_past:
                trend = 1
            if close_now < green_line_past:
                trend = -1
            if trend > 0:
                self.supertrend.append(green_line)
            else:
                self.supertrend.append(red_line)
            close_past = close_now
            red_line_past = red_line
            green_line_past = green_line

        return self.supertrend

    def indicator_macd(self, fast=12, slow=26, signal_smoothing=9):
        self.macd = [x - y for x, y in zip(self.indicator_ema(self.close, fast), self.indicator_ema(self.close, slow))]
        self.signal = self.indicator_ema(self.macd, signal_smoothing)
        return self.macd, self.signal

    def indicator_dmi(self, smooth=14, length=14):
        max_past = float(self.max[1])
        min_past = float(self.min[1])
        close_past = float(self.close[0])
        plus_dm_list = []
        minus_dm_list = []
        tr_list = []
        for i in self.klines:
            max_now = float(i[2])
            min_now = float(i[3])
            close_now = float(i[4])
            plus_m = max_now - max_past
            minus_m = min_past - min_now
            if plus_m > minus_m and plus_m > 0:
                plus_dm_list.append(plus_m)
            else:
                plus_dm_list.append(0)
            if minus_m > plus_m and minus_m > 0:
                minus_dm_list.append(minus_m)
            else:
                minus_dm_list.append(0)
            tr_list.append(max(max_now, close_past) - min(min_now, close_past))
            max_past = max_now
            min_past = min_now
            close_past = close_now
        tr_rma = self.indicator_rma(tr_list, length)
        self.plus_di = [100 * (x / y) for x, y in zip(self.indicator_rma(plus_dm_list, length), tr_rma)]
        self.minus_di = [100 * (x / y) for x, y in zip(self.indicator_rma(minus_dm_list, length), tr_rma)]
        self.adx = self.indicator_rma([100 * (abs(x - y) / (x + y)) for x, y in zip(self.plus_di, self.minus_di)],
                                      smooth)
        return self.adx

    def indicator_rsi(self):
        pass
