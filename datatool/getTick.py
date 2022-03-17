import gqdb_sdk
from gqdb_sdk import client
from gqdb_sdk.constant import Frequency,Market,Source,MarketDataType,DataType,TimestampType,MetaData
from wtpy.ExtModuleDefs import BaseExtDataLoader
from ctypes import POINTER
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
import pandas as pd
import random
from wtpy import WtEngine,WtBtEngine,EngineType
import datetime as dt
from tqdm import tqdm
import os
from wtpy.wrapper import WtDataHelper
import rqdatac as rq
from joblib import Parallel, delayed

# class GqdbFeed(object):
#     def __init__(self,host,port,user,passwd):
#         # 后面自己改
#         s = client.session(host="192.168.0.132")
        
#     def get_price(self,symbol,freq,start_date,end_date):
#         df = s.get_price(symbol,frequency)

# 将代码转成gqdb里的标准代码
def cover_gqdb_code(symbol):
    exchange = symbol.split(".")[0]
    pid = symbol.split(".")[1]

# 根据交易所来确定大小写
def format_code(exchange,pid,month):
    if exchange == "CZCE":
        pid = pid.upper()
        month = month[-3:]
        return exchange,pid,month
    else:
        pid = pid.lower()
        return exchange,pid,month

def get_tick_from_gqdb(code,start_date,end_date,skip_saved=True,to_dsb=False):
    s = client.session(host="192.168.0.132")
    info_df = s.all_instruments("Future")
    info_df = info_df[info_df["de_listed_date"]!="0000-00-00"]
    info_df["de_listed_date"] = pd.to_datetime(info_df["de_listed_date"])
    info_df = info_df[(info_df["de_listed_date"]>start_date) &  (info_df["de_listed_date"]<end_date)]
    save_path = "./csv"
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    saved_l = os.listdir(save_path)
    saved_l = [".".join(i.split(".")[:-1]) for i in saved_l]

    exchange = code.split(".")[0]
    pid = code.split(".")[1]
    symbols = info_df[info_df["underlying_symbol"]==pid.upper()][["order_book_id","contract_multiplier"]]
    print(f"{pid} start")
    for index,row in tqdm(symbols.iterrows()):
        symbol = row["order_book_id"]
        month = symbol[-4:]
        exchange,pid,month = format_code(exchange,pid,month)
        stdcode = f"{exchange}.{pid}.{month}"
        code = f"{pid}{month}"
        # 分天，避免内存超出
        for date in pd.date_range(start_date,end_date):
            file_name = f"{stdcode}_tick_{date.strftime('%Y%m%d')}"
            if skip_saved:
                if file_name in saved_l:
                    print(f"{file_name}已存在，跳过")
                    continue
            df = s.get_price(symbol,frequency="Tick",start_date=date.strftime('%Y.%m.%d'),end_date=date.strftime('%Y.%m.%d'))

            if df.empty:
                continue
            multiplier = row["contract_multiplier"]
            df = df.reset_index()
            df["code"] = code
            df["exchg"] = exchange
            df["pre_interest"] = 0
            df["settle"] = ((df["total_turnover"] / df["volume"]) * multiplier).fillna(0.0)
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["trading_date"] = pd.to_datetime(df["trading_date"])
            df["date"] = df["datetime"].dt.date
            df["time"] = df["datetime"].dt.time
            df["date"] = pd.to_datetime(df["date"])
            #改一下格式
            df["trading_date"] =  df["trading_date"].dt.strftime("%Y%m%d")
            df["date"] =  df["date"].dt.strftime("%Y%m%d")
            df["time"] =  df["time"].astype("str")
            time_df = df["time"].str.split(".",expand=True)
            if len(time_df.columns)==1:
                df["time"] = df["time"].str.replace(":","").astype("int")*1000
            else:
                time_df[1] = time_df[1].fillna(0).astype("int")/1000
                time = time_df[0].str.replace(":","").astype("int")*1000 + time_df[1]
                time = time.astype("int")
                df["time"] = time

            # 改名，与cpp的格式一致
            col_map = {
                "exchg":"exchg",
                "code":"code",
                "last":"price",
                "open":"open",
                "high":"high",
                "low":"low",
                "settle":"settle",
                "volume":"total_volume",
                "total_turnover":"total_turnover",
                "open_interest":"open_interest",
                "trading_date":"trading_date",
                "date":"action_date",
                "time":"action_time",
                "prev_close":"pre_close",
                "prev_settlement":"pre_settle",
                "pre_interest":"pre_interest",
            }
            
            for i in range(1,6):
                col_map[f"a{i}"] = f"ask_{i}"
                col_map[f"b{i}"] = f"bid_{i}"
                col_map[f"a{i}_v"] = f"ask_qty_{i}"
                col_map[f"b{i}_v"] = f"bid_qty_{i}"
                
            df = df[col_map.keys()]
            df = df.rename(columns=col_map)
            path = os.path.join(save_path,f"{file_name}.csv")
            df.to_csv(path,index=None)
            
            if to_dsb:
                len_df = len(df)
                BUFFER = WTSTickStruct*len_df
                buffer = BUFFER()
                # 填充数据
                i = -1
                for _,d_row in df.iterrows():
                    i+=1
                    curTick = buffer[i]
                    curTick.exchg = bytes(d_row["exchg"],'utf-8') 
                    curTick.code = bytes(d_row["code"],'utf-8') 
                    curTick.price = float(d_row["price"])
                    curTick.open = float(d_row["open"])
                    curTick.high = float(d_row["high"])
                    curTick.low = float(d_row["low"])
                    curTick.settle = float(d_row["settle"])
                    curTick.total_volume = int(d_row["total_volume"])
                    curTick.total_turnover = float(d_row["total_turnover"])
                    curTick.open_interest = int(d_row["open_interest"])
                    # 时间处理
                    curTick.trading_date = int(d_row["trading_date"])
                    curTick.action_date = int(d_row["action_date"])
                    curTick.action_time = int(d_row["action_time"])

                    curTick.pre_close = float(d_row["pre_close"])
                    curTick.pre_settle = float(d_row["pre_settle"])
                    curTick.pre_interest = int(d_row["pre_interest"])

                    for x in range(1,6):
                        curTick.bid_prices[x] = float(d_row["bid_" + str(x)])
                        curTick.bid_qty[x] = int(d_row["bid_qty_" + str(x)])
                        curTick.ask_prices[x] = float(d_row["ask_" + str(x)])
                        curTick.ask_qty[x] = int(d_row["ask_qty_" + str(x)])
                        
                path = os.path.join("./bin",f"{file_name}.dsb")
                dtHelper.store_ticks(path, buffer, len_df)
            print(f"{file_name}已保存")
        print(f"{symbol} tick 转存完毕")


def get_tick_from_rq(codes,start_date,end_date):
    rq.init()
    info_df = rq.all_instruments("Future")
    info_df = info_df[info_df["de_listed_date"]!="0000-00-00"]
    info_df["de_listed_date"] = pd.to_datetime(info_df["de_listed_date"])
    info_df = info_df[(info_df["de_listed_date"]>start_date) &  (info_df["de_listed_date"]<end_date)]

    for code in codes:
        exchange = code.split(".")[0]
        pid = code.split(".")[1]
        symbols = info_df[info_df["underlying_symbol"]==pid.upper()][["order_book_id","contract_multiplier"]]
        print(f"{pid} start")
        for index,row in tqdm(symbols.iterrows()):
            symbol = row["order_book_id"]
            df = rq.get_price(symbol,frequency="tick",start_date=start_date,end_date=end_date)
            month = symbol[-4:]
            code = f"{exchange}.{pid}.{month}"
            exchange,pid,month = format_code(exchange,pid,month)
            multiplier = row["contract_multiplier"]
            df = df.reset_index()
            df["settle"] = ((df["total_turnover"] / df["volume"]) * multiplier).fillna(0.0)
            df["datetime"] = pd.to_datetime(df["datetime"])
            df["trading_date"] = pd.to_datetime(df["trading_date"])
            df["date"] = df["datetime"].dt.date
            df["time"] = df["datetime"].dt.time
            df["date"] = pd.to_datetime(df["date"])
            #改一下格式
            df["trading_date"] =  df["trading_date"].dt.strftime("%Y%m%d")
            df["date"] =  df["date"].dt.strftime("%Y%m%d")
            df["time"] =  df["time"].astype("str")
            time_df = df["time"].str.split(".",expand=True)
            time_df[1] = time_df[1].fillna(0).astype("int")/1000
            time = time_df[0].str.replace(":","").astype("int")*1000 + time_df[1]
            time = time.astype("int")
            df["time"] = time
            
            # 按照交易日分割
            g = df.groupby("trading_date")
            for trading_date,g_df in g:
                len_df = len(g_df)
                BUFFER = WTSTickStruct*len_df
                buffer = BUFFER()
                # 填充数据
                i = -1
                for _,d_row in g_df.iterrows():
                    i+=1
                    curTick = buffer[i]
                    curTick.exchg = bytes(exchange,'utf-8') 
                    curTick.code = bytes(code,'utf-8') 
                    curTick.price = float(d_row["last"])
                    curTick.open = float(d_row["open"])
                    curTick.high = float(d_row["high"])
                    curTick.low = float(d_row["low"])
                    curTick.settle = float(d_row["settle"])
                    curTick.total_volume = int(d_row["volume"])
                    curTick.total_turnover = float(d_row["total_turnover"])
                    curTick.open_interest = int(d_row["open_interest"])
                    # 时间处理
                    curTick.trading_date = int(d_row["trading_date"])
                    curTick.action_date = int(d_row["date"])
                    curTick.action_time = int(d_row["time"])

                    curTick.pre_close = float(d_row["prev_close"])
                    curTick.pre_settle = float(d_row["prev_settlement"])
                    curTick.pre_interest = int(0)

                    for x in range(1,6):
                        curTick.bid_prices[x] = float(d_row["a" + str(x)])
                        curTick.bid_qty[x] = int(d_row["a" + str(x) + "_v"])
                        curTick.ask_prices[x] = float(d_row["b" + str(x)])
                        curTick.ask_qty[x] = int(d_row["b" + str(x) + "_v"])
                    
                path = os.path.join(save_path,f"{code}_tick_{trading_date}.dsb")
                dtHelper.store_ticks(path, buffer, len_df)
            print(f"{symbol} tick 转存完毕")
            
if __name__ == "__main__":
    codes = ["SHFE.al", "SHFE.cu", "SHFE.ru", "DCE.m", "DCE.a", "CZCE.CF", "DCE.c", "CZCE.SR", "DCE.y",
    "CZCE.TA","SHFE.zn", "CZCE.OI", "DCE.l", "DCE.p", "SHFE.rb", "CZCE.MA", "CZCE.RM", "DCE.i", "DCE.pp",
    "SHFE.ni"]
    dtHelper = WtDataHelper()
    save_path = "./bin"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    csv_path = "./csv"
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    start_date = dt.datetime(2021,1,1)
    end_date = dt.datetime(2022,12,1)
    for code in codes:
        get_tick_from_gqdb(code, start_date, end_date)

    # Parallel(n_jobs=2)(
    #     delayed(get_tick_from_gqdb)(code, start_date,end_date) for code in codes)


    