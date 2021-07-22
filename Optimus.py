from telethon.errors import SessionPasswordNeededError
from telethon import TelegramClient, events, sync
from telethon.hints import MessageLike
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
PeerChannel
)
import requests
import NFO_expiry_calc
import playsound
from fyers_main import Fyers_Symbol, Fyers_Orders
import config

Lots = config.user_detail['lots']
EQ_bot_token = "1555749245:AAF3xYiG7O88WFKOqCXFNLCBMenOpbEiDgA"
EQ_bot_chat_ids = ['903638978']
#####TO BE CONFIGURED
tele_api_id = None #< YOUR TELEGRAM APP ID > 
tele_api_hash = None #< YOUR TELEGRAM HASH >
#=================================
client = TelegramClient('anon', tele_api_id, tele_api_hash)
user_input_channels = ['https://t.me/EGQbot'] #Listens to Eaglequant bot for any messages to execute.
print("Telegram bot is listening")
#=================================

def get_instru(splits, a):
    instru = splits[a]
    if instru[0] != '#':
        instru = '#' + instru
    a += 1
    if not instru:
        instru = get_instru(splits, a)
    return instru

def get_option_symbol(signal, ins, strike, opt_type):
    expiry = NFO_expiry_calc.getNearestWeeklyExpiryDate()
    print(f"signal: {signal}, {ins}, {strike+opt_type}, {expiry}")
    if opt_type == 'CE' or opt_type == 'CALL':
        symbole = Fyers_Symbol(ins, strike, opt_type, expiry)
        symbolee = symbole.get_symbol()
    elif opt_type == 'PE' or opt_type == 'PUT':
        symbole = Fyers_Symbol(ins, strike, opt_type, expiry)
        symbolee = symbole.get_symbol()
    qty = int(symbole.get_lotsize() * Lots)
    print(symbolee, qty)
    return symbolee, qty, expiry

@client.on(events.NewMessage(chats=user_input_channels))
async def newMessageListener(event):
    newMessage = event.message.message
    print(newMessage)
    splits = newMessage.split(' ')
    if splits[0][0] == '#':
        splits[0:0] = ['buy']
    instru = get_instru(splits, 1)
    signal = splits[0].upper()
    if signal=='BUY' or signal=='SELL':
        if instru[0]=='#':
            ins = instru[1:].upper()
            if ins == 'NIFTY' or ins == 'BANKNIFTY':
                strike = splits[2]
                if len(strike) != 5:
                    opt_type = strike[5:].upper()
                    strike = strike[:5]
                else:
                    opt_type = splits[3].upper()
                if ins == 'NIFTY':
                    trigger = 6.0
                elif ins == 'BANKNIFTY':
                    trigger = 10.0
                symbolee, qty, expiry = get_option_symbol(signal, ins, strike, opt_type)
                if signal == 'BUY':
                    res, id = Fyers_Orders.market_buy_order_MIS(symbolee, qty)
                    res2 = Fyers_Orders.place_Auto_SLM(id, qty, trigger, signal)
                    print(res2)
                elif signal == 'SELL':
                    res, id = Fyers_Orders.market_sell_order_MIS(symbolee, qty)
                    res2 = Fyers_Orders.place_Auto_SLM(id, qty, trigger, signal)
                messa = res + ' For ' + ins + strike + opt_type + ' Expiry ' + str(expiry)
                playsound.playsound('D:/ProjectT/Quickey/Optimus/notify/duck_hunt.mp3', True)
                tele_url = f'https://api.telegram.org/bot{ EQ_bot_token }/sendMessage'   
                
                for chat_id in EQ_bot_chat_ids:
                    payload = {'chat_id': chat_id, 'text': messa}
                    r = requests.post(tele_url, data=payload)
                    continue
                print("Listening for Next message.......")
            else:
                print(f"signal {signal}: {ins}")
                print("Not Options")
                print("Listening for Next message.......")
        else:
            pass
    else:
        print("Junk Message")
        print("Listening for Next message.......")
    
with client:
    client.run_until_disconnected()
    

