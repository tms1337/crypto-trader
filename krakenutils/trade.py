import krakenex
from .providerbase import PrivateProviderBase


class TradeProvider(PrivateProviderBase):
    def __init__(self, api_key, currency, crypto, api=krakenex.API()):
        super(TradeProvider, self).__init__(api_key, currency, crypto, api)

    def create_offer(self):
        pass

    def total_balance(self):
        balance_response = self.k.query_private('Balance')
        self._check_response(balance_response)

        orders_response = self.k.query_private('OpenOrders')
        self._check_response(orders_response)

        balance = balance_response['result']
        orders = orders_response['result']

        newbalance = dict()
        for currency in balance:
            # remove first symbol ('Z' or 'X')
            newname = currency[1:] if len(currency) == 4 else currency
            newbalance[newname] = float(balance[currency])
        balance = newbalance

        for _, o in orders['open'].items():
            # base volume
            volume = float(o['vol']) - float(o['vol_exec'])

            # extract for less typing
            descr = o['descr']

            # order price
            price = float(descr['price'])

            pair = descr['pair']
            base = pair[:3]
            quote = pair[3:]

            type_ = descr['type']
            if type_ == 'buy':
                # buying for quote - reduce quote balance
                balance[quote] -= volume * price
            elif type_ == 'sell':
                # selling base - reduce base balance
                balance[base] -= volume

        return balance