import json
import pandas as pd
import datetime as dt
from datetime import datetime
from fyers_api import fyersModel, accessToken
import sys
import requests
import csv
import re
import orders_model
from pandas.core.indexes.base import Index

#####TO BE CONFIGURED
mainfolder = None #<YOUR PROJECT FOLDER>

df3 = pd.DataFrame()
symbol_file = '{}/temp/fyers_symbols.csv'.format(mainfolder)
url = 'http://public.fyers.in/sym_details/NSE_FO.csv'
columns = ['instrument', 'name', 'A', 'lot_size', 'tick', 'B', 'C', 'date', 'time', 'symbol', 'D', 'E', 'num', 'symbol_name']
df = pd.read_csv(url, names =columns, header=None)
nms = ['BANKNIFTY', 'NIFTY']
df3 = df[df['symbol_name'].isin(nms)]
df3.to_csv(symbol_file)

def get_token(app_id, app_secret, fyers_id, password, pan_dob):
    appSession = accessToken.SessionModel(app_id, app_secret)
    response = appSession.auth()
    if response["code"] != 200:
        return response
        # sys.exit()
    auth_code = response["data"]["authorization_code"]

    appSession.set_token(auth_code)

    generateTokenUrl = appSession.generate_token()
    # webbrowser.open(generateTokenUrl, new=1)
    headers = {
        "accept": "*/*",
        "accept-language": "en-IN,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json; charset=UTF-8",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referrer": generateTokenUrl
    }
    payload = {"fyers_id": fyers_id, "password": password,
               "pan_dob": pan_dob, "appId": app_id, "create_cookie": False}
    result = requests.post("https://api.fyers.in/api/v1/token",
                           headers=headers, json=payload, allow_redirects=True)
    if result.status_code != 200:
        print("Error Loging into Fyers")
        return
    # print(result.json())
    result_url = result.json()["Url"]
    token_re = re.search(r'access_token=(.*?)&', result_url, re.I)
    if token_re:
        return token_re.group(1)
    return "error"

try:
    user = json.loads(open('{}/config/userinfo.json'.format(mainfolder), 'r').read().strip())
    # NOTE Contents of userinfo.json
    access_token = get_token(app_id=user['fyers_app_id'], app_secret=user['fyers_app_secret'],
                            fyers_id=user['fyers_id'], password=user['fyers_password'], pan_dob=user['fyers_pan_or_dob'])
    try:
        fyers = fyersModel.FyersModel()
        fyers.positions(token=access_token)
        print("Fyers Login Successfull")
    except:
        sys.exit("Login Failed for Fyers")
except:
    sys.exit("Login Failed for Fyers")

tick_round = lambda x: round(0.05*round(x/0.05), 2)
    
def fetch_position_ids():
    try:
        open_response = fyers.positions(token=access_token) # Access positions
        positions = open_response['data']['netPositions']
        actv_positions_ids = [position['id'] for position in positions if abs(position['netQty']) > 0 \
            and position['productType'] =='INTRADAY']
        return actv_positions_ids
    except:
        print("Glitch fetching positions")
        return fetch_position_ids()

class Fyers_Symbol:
    def __init__(self, ins, strike, opt, expiry):
        self.inst = ins
        self.exp = str(expiry)
        self.strike = strike
        self.opt = opt
    def get_symbol(self):
        symbol_file = '{}/temp/fyers_symbols.csv'.format(mainfolder)
        df3 = pd.read_csv(symbol_file)
        ex_dt = datetime.strptime(self.exp, '%Y-%m-%d').strftime('%y %b %d')
        nome = self.inst + ' ' + ex_dt + ' ' + str(self.strike) + ' ' + self.opt
        row = df3.loc[(df3['name']==nome)]
        symbol = row['symbol'].to_list()
        return symbol[0]
    def get_lotsize(self):
        symbol_file = '{}/temp/fyers_symbols.csv'.format(mainfolder)
        df3 = pd.read_csv(symbol_file)
        ex_dt = datetime.strptime(self.exp, '%Y-%m-%d').strftime('%y %b %d')
        nome = self.inst + ' ' + ex_dt + ' ' + str(self.strike) + ' ' + self.opt
        row = df3.loc[(df3['name']==nome)]
        lot_size = row['lot_size'].to_list()
        return lot_size[0]

class Fyers_Orders:
    def exit_all_position(): 
        ids =  fetch_position_ids()
        try:
            for id in ids:
                exit_pos = orders_model.exit_position(id)
                jsondata = exit_pos.getJsonStructure()
                fyers.exit_positions(token=access_token, data = jsondata)
            return 'All Positions Exited'
        except:
            return 'No Positions to Exit'

    def market_sell_order_MIS(symbol, qty):
        sell_order = orders_model.place_orders()
        sell_order.setSymbol(symbol)
        sell_order.setqty(qty)
        sell_order.setside(-1)
        sell_order.setType(2)
        jsondata = sell_order.getJsonStructure()
        response = fyers.place_orders(token=access_token, data = jsondata)
        return response['message'], response['data']['id']

    def market_buy_order_MIS(symbol, qty):
        sell_order = orders_model.place_orders()
        sell_order.setSymbol(symbol)
        sell_order.setqty(qty)
        sell_order.setside(1)
        sell_order.setType(2)
        jsondata = sell_order.getJsonStructure()
        response = fyers.place_orders(token=access_token, data = jsondata)
        return response['message'], response['data']['id']

    def place_SLM_for_sell_MIS(symbol, qty, stop_price):
        SLM_order = orders_model.place_orders()
        SLM_order.setSymbol(symbol)
        SLM_order.setqty(qty)
        SLM_order.setside(1)
        SLM_order.setType(3)
        SLM_order.setstopPrice(stop_price)
        jsondata = SLM_order.getJsonStructure()
        response = fyers.place_orders(token=access_token, data = jsondata)
        return response['message']

    def place_SLM_for_buy_MIS(symbol, qty, stop_price):
        SLM_order = orders_model.place_orders()
        SLM_order.setSymbol(symbol)
        SLM_order.setqty(qty)
        SLM_order.setside(-1)
        SLM_order.setType(3)
        SLM_order.setstopPrice(stop_price)
        jsondata = SLM_order.getJsonStructure()
        response = fyers.place_orders(token=access_token, data = jsondata)
        return response['message']

    def update_SLM__sell_price(order_id, qty, upd_price):
        SLM_modify = orders_model.update_orders(order_id)
        SLM_modify.upd_stopPrice(upd_price)
        SLM_modify.upd_qty(qty)
        jsondata = SLM_modify.getJsonStructure()
        response = fyers.update_orders(token=access_token, data = jsondata)
        return response['message'], response['data']['id']
    
    def place_Auto_SLM(order_id, opt_qty, trigger, signal):
        try:
            resp = fyers.tradebook(token = access_token)
            trades = resp['data']['tradeBook']
            ord_info = [{'symbol' : trade['symbol'],'trd_prc' : trade['tradePrice']} for trade in trades if trade['orderNumber'] == order_id]
            if signal == 'BUY':
                sell_prc = ord_info[0]['trd_prc'] - trigger
                sell_price = tick_round(sell_prc)
                res = Fyers_Orders.place_SLM_for_buy_MIS(ord_info[0]['symbol'], opt_qty, sell_price)
                return f"Placed SLM sell for {ord_info[0]['symbol']} : {res}"
            elif signal == 'SELL':
                buy_prc = ord_info[0]['trd_prc'] + trigger
                buy_price = tick_round(buy_prc)
                res = Fyers_Orders.place_SLM_for_sell_MIS(ord_info[0]['symbol'], opt_qty, buy_price)
                return f"Placed SLM buy for {ord_info[0]['symbol']} : {res}"
        except:
            return "Error placing SLM"


