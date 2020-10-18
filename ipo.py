class Broker(object):
    name = ''
    cash_subscription_fee = 100
    financing_subscription_fee = 100
    financing_rate = 0.03
    financing_multiple = 10

    def __init__(self, name, **kw):
        self.name = name
        self.cash_subscription_fee = kw.get('cash_subscription_fee', 100)
        self.financing_subscription_fee = kw.get('financing_subscription_fee', 100)
        self.financing_rate = kw.get('financing_rate', 0.03)
        self.financing_multiple = kw.get('financing_multiple', 10)

    def description(self):
        desc = self.name
        desc = desc + ' ' + ' 现金申购费:' + str(self.cash_subscription_fee)
        desc = desc + ' ' + ' 融资申购费:' + str(self.financing_subscription_fee)
        desc = desc + ' ' + ' 融资利率:' + str(self.financing_rate)
        desc = desc + ' ' + ' 融资倍数:' + str(self.financing_multiple)
        return desc
        
class Stock(object):
    name = ''
    ipo_price = 1
    freeze_day_cnt = 3
    growth_rate = 0.1
    lot_winning_rate = 0.03
    winning_rate_growth = 0.007

    def __init__(self, name, ipo_price, **kw):
        self.name = name
        self.ipo_price = ipo_price
        self.freeze_day_cnt = kw.get('freeze_day_cnt', 3)
        self.growth_rate = kw.get('growth_rate', 0.1)
        self.lot_winning_rate = kw.get('lot_winning_rate', 0.03)
        self.winning_rate_growth = kw.get('winning_rate_growth', 0.007)

    def winning_rate(self, lot_cnt):
        if lot_cnt == 1:
            return self.lot_winning_rate
        else:
            return self.lot_winning_rate + (lot_cnt - 1) * self.winning_rate_growth

    def valid_lot_cnt(self, lot_cnt):
        lot_cnt_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 400, 600, 800]
        result = 0
        for i in lot_cnt_array:
            if i <= lot_cnt:
                result = i
            else:
                break
        return result
    
    def description(self):
        desc = self.name
        desc = desc + ' ' + ' 价格:' + str(self.ipo_price)
        desc = desc + ' ' + ' 冻资天数:' + str(self.freeze_day_cnt)
        desc = desc + ' ' + ' 增长率:' + str(self.growth_rate)
        desc = desc + ' ' + ' 一手中签率:' + str(self.lot_winning_rate)
        desc = desc + ' ' + '中签率增长:' + str(self.winning_rate_growth)
        return desc


class IPOScheme(object):
    def __init__(self, stock, broker, cash, use_financing):
        self.stock = stock
        self.broker = broker
        self.cash = cash
        self.use_financing = use_financing
        self.cash_lot = self.stock.valid_lot_cnt(int(self.cash / self.stock.ipo_price))
        self.financing_lot = self.stock.valid_lot_cnt(int(self.cash * self.broker.financing_multiple / self.stock.ipo_price))
        self.logs = []
        self.cost = IPOCost(stock, broker, cash = cash, use_financing = use_financing, cash_lot = self.cash_lot, financing_lot = self.financing_lot)
        lot = self.financing_lot if self.use_financing else self.cash_lot
        self.earnings = IPOEarnings(stock, broker, cash = cash, use_financing = use_financing, lot = lot)

    def profit(self):
        self.logs.clear()
        self.logs.append('融资申购') if self.use_financing else self.logs.append('现金申购') 
        cost_result = self.cost.calc()
        self.logs.append('========成本:' + str(cost_result))
        self.logs.extend(self.cost.description())
        earnings_result = self.earnings.calc()
        self.logs.append('========营收:' + str(earnings_result))
        self.logs.extend(self.earnings.description())
        profit_result = earnings_result - cost_result
        self.logs.append('========盈利:' + str(profit_result))
        return profit_result

    def description(self):
        desc = ''
        for log in self.logs:
            desc = desc + log + '\n'
        return desc


class IPOCost(object):
    def __init__(self, stock, broker, **kw):
        self.details = []
        self.stock = stock
        self.broker = broker
        self.cash = kw.get('cash', 0)
        self.cash_lot = kw.get('cash_lot', 0)
        self.financing_lot = kw.get('financing_lot', 0)
        self.use_financing = kw.get('use_financing', 0)

    def calc(self):
        self.details.clear()
        if not self.use_financing:
            self.details.append('现金申购费:' + str(self.broker.cash_subscription_fee))
            all_cost = self.broker.cash_subscription_fee
            return all_cost
        
        pure_financing_lot = self.financing_lot * ( self.broker.financing_multiple - 1)  / self.broker.financing_multiple
        self.details.append('纯融资手数:' + str(pure_financing_lot))
        pure_financing_money = pure_financing_lot * self.stock.ipo_price
        self.details.append('融资额:' + str(pure_financing_money))
        financing_cost = pure_financing_money * self.broker.financing_rate * self.stock.freeze_day_cnt / 365.0
        self.details.append('融资费用:' + str(financing_cost))
        self.details.append('融资申购费:' + str(self.broker.financing_subscription_fee))
        all_cost = financing_cost + self.broker.financing_subscription_fee
        return all_cost
    
    def description(self):
        return self.details


class IPOEarnings(object):
    def __init__(self, stock, broker, **kw):
        self.stock = stock
        self.broker = broker
        self.cash = kw.get('cash', 0)
        self.use_financing = kw.get('use_financing', 0)
        self.lot = kw.get('lot', 0)
        self.details = []
    
    def calc(self):
        self.details.clear()
        self.details.append('总手数:' + str(self.lot))
        winning_rate = self.stock.winning_rate(self.lot)
        self.details.append('中签率' + str(winning_rate))
        earnings = self.stock.ipo_price * winning_rate * self.stock.growth_rate
        self.details.append('单手价格' + str(self.stock.ipo_price))
        self.details.append('增长' + str(self.stock.growth_rate))
        return earnings

    def description(self):
        return self.details
    
class IPOArrange(object):
    def __init__(self, stock, cash, broker_list, **kw):
        self.stock = stock
        self.broker_list = broker_list
        self.cash = cash
        self.all_scheme_list = []
    
    def arrange(self):
        self.arrange_impl([], 0)
        the_profit = 0
        the_scheme_list = None
        for current_scheme_list in self.all_scheme_list:
            current_profit = 0
            desc = ''
            for scheme in current_scheme_list:
                current_profit = current_profit + scheme.profit()
                # desc = desc + scheme.broker.name + str(scheme.cash) + ' ' + str(scheme.use_financing) + '\n'
            # print(desc + str(current_profit) + '\n')

            if (current_profit > the_profit):
                the_profit = current_profit
                the_scheme_list = current_scheme_list
        
        logs = []
        desc = ''
        for scheme in the_scheme_list:
            desc = desc + scheme.broker.name + str(scheme.cash) + ' ' + str(scheme.use_financing) + '\n'
            logs.append(scheme.broker.name + scheme.description())
        print(desc + str(the_profit) + '\n')

        for log in logs:
            print(log)


        
        return the_scheme_list

    def arrange_impl(self, current_scheme_list, layer):
        sum = 0
        for scheme in current_scheme_list:
            sum = sum + scheme.cash
        
        if (sum > self.cash):
            return
        elif sum == self.cash:
            copy_list = []
            copy_list.extend(current_scheme_list)
            self.all_scheme_list.append(copy_list)
            return
        
        if layer >= len(self.broker_list):
            copy_list = []
            copy_list.extend(current_scheme_list)
            self.all_scheme_list.append(copy_list)
            return

        k = 0
        while k + sum <= self.cash:
            if k == 0:
                self.arrange_impl(current_scheme_list, layer + 1)
            else:
                scheme = IPOScheme(self.stock, self.broker_list[layer], k, 0)
                current_scheme_list.append(scheme)
                self.arrange_impl(current_scheme_list, layer + 1)
                current_scheme_list.pop()

                scheme = IPOScheme(self.stock, self.broker_list[layer], k, 1)
                current_scheme_list.append(scheme)
                self.arrange_impl(current_scheme_list, layer + 1)
                current_scheme_list.pop()

            k = k + self.stock.ipo_price
        


stock = Stock('测试股票', 10700, freeze_day_cnt = 5, growth_rate = 0.06, lot_winning_rate = 0.05, winning_rate_growth = 0.007)
print(stock.description())

broker_list = []
broker_list.append(Broker('老虎'))
broker_list.append(Broker('富途', cash_subscription_fee = 50))
broker_list.append(Broker('辉立', cash_subscription_fee = 0, financing_subscription_fee = 0))
broker_list.append(Broker('华泰', cash_subscription_fee = 0, financing_subscription_fee = 0))
broker_list.append(Broker('艾德', cash_subscription_fee = 0))
broker_list.append(Broker('耀才', cash_subscription_fee = 0))
for broker in broker_list:
    print(broker.description())

a = IPOArrange(stock, 140000, broker_list)
a.arrange()