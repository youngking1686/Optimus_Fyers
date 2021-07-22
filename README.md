# Optimus_Fyers
Telegram to Fyers order bot

Run the Optimus.py from cmd to start the bot.
Bot listens to the telegram account configured and sends orders to Fyers.

### SETTINGS:
set Telegram details:
open Optimus.py --> Find #####TO BE CONFIGURED section and update "tele_api_id" , "tele_api_hash" and add your Telegram api id and api hash.
set mainfolder:
open fyers_main --> Find #####TO BE CONFIGURED section and update the "mainfolder" with current project folder. eg: "D:/projects/Optimus_Fyers"
set StopLoss trigger limit:
to change the stoploss trigger levels find variable named "trigger" in Optimus.py (default, Nifty: 8, Banknifty:10)

** Only Works for Options, not futures, not equity
** Places orders only for immediate weekly options.
** Places Market orders and places SLM orders with default trigger values 
### Following Command structures work:
examples:
buy nifty 15600 ce
buy NIFTY 15600CE
Buy #NIFTY 15600 CE
BUY NIFTY 15600CE
===
SELL NIFTY 15600CE
sell nifty 15600 ce
sell NIFTY 15600CE
Sell #NIFTY 15600 CE

