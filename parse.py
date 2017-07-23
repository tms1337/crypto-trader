import matplotlib.pyplot as plt

values = []

while True:
    try:
        line = input("")
        start_btc = line.find(":")
        start_btc = line.find(":", start_btc + 1)
        start_btc = line.find(":", start_btc + 1)
        start_usd = line.find(":", start_btc + 1)

        after_btc = line[start_btc + 2:]
        btc_value = float(after_btc[:after_btc.find(",")])
        after_usd = line[start_usd + 2:]
        usd_value = float(after_usd[:after_usd.find("}")])

        values.append(btc_value * 2851 + usd_value)
    except:
        break

print(len(values))

plt.plot(values)
plt.show()
