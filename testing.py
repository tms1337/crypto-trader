currencies = ["BTC"]
trading_currency = ["USD"]



ExchangeDiffOfferDecider(currencies=currencies, trading_currency=trading_currency)


for i in range(len(last_array)):
    decisions = []
    decider.decide(decisions)
    for d in decisions:
        d.decider.apply_last()
    print(decisions)
