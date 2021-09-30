# PredictionV2-bot
PancakeSwap Prediction V2 Player Bot [PYTHON]

Requirements:

```
pip install web3
```

Settings:

```python
# YOU
ADDRESS = w3.toChecksumAddress('ADDRESS')
PRIVATE_KEY = str('PRIVATE_KEY').lower()

# TX SETTING
GAS = 400000
GAS_PRICE = 5000000000

# SECONDS LEFT BET AT
SECONDS_LEFT = 8
```

Bet Config:

```python
def makeBet(epoch):
    """
    Add your bet logic here
    This example bet random either up or down:
    """
    value = w3.toWei(0.01, 'ether')
    rand = random.getrandbits(1)
    if rand:
        betBull(value, epoch)
        print(f'Going Bull #{epoch} | {value} BNB  ')
    else:
        betBear(value, epoch)
        print(f'Going Bear #{epoch} | {value} BNB  ')
```




