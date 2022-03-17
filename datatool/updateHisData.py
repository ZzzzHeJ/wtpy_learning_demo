from distutils.log import info
from dataFeed import GqdbFeed,RqFeed
import rqdatac as rq
import datetime as dt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED

import multiprocessing
from tqdm import tqdm
# rqFeed = RqFeed()
gqFeed = GqdbFeed(host="192.168.0.132")
storage_path = r"\\WIN-52AMQLH0TIA\WonderTrader\storage"
def update_bar(row):
    feed = RqFeed()
    symbol = row["order_book_id"]
    pid = row["underlying_symbol"]
    month = symbol.replace(pid,"")
    exchange = row["exchange"]
    if exchange == "CZCE" or exchange == "CFFEX":
        pid = pid.upper()
    else:
        pid = pid.lower()
    code = f"{exchange}.{pid}.{month}"
    #分别下载日线，分钟线，tick
    s = row["listed_date"]
    e = row["de_listed_date"]
    feed.store_his_bar(storage_path,code,s,e,"d",True)
    feed.store_his_bar(storage_path,code,s,e,"m1",True)

def update_tick(row):
    feed = GqdbFeed(host="192.168.0.132")
    symbol = row["order_book_id"]
    pid = row["underlying_symbol"]
    month = symbol.replace(pid,"")
    exchange = row["exchange"]
    if exchange == "CZCE" or exchange == "CFFEX":
        pid = pid.upper()
    else:
        pid = pid.lower()
    code = f"{exchange}.{pid}.{month}"
    #分别下载日线，分钟线，tick
    s = row["listed_date"]
    e = row["de_listed_date"]
    feed.store_his_tick(storage_path,code,s,e,True)
    try:
        with open("saved.txt","a") as f:
            f.write(f"{symbol}\n")
    except:
        pass

if __name__ == "__main__":
    need_l = ["AL", "CU", "RU", "M", "A", "CF", "C", "SR","Y",
                "TA","ZN", "OI", "L", "P", "RB", "MA", "RM", "I", "PP","NI"]
    start_date = dt.datetime(2020,1,1)
    end_date = dt.datetime.now()
    info_df_list = []
    rq.init()
    for date in pd.date_range(start_date,end_date):
        info_df = rq.all_instruments("Future")
        info_df = info_df[info_df["de_listed_date"]!="0000-00-00"]
        info_df["de_listed_date"] = pd.to_datetime(info_df["de_listed_date"])
        info_df = info_df[info_df["listed_date"]!="0000-00-00"]
        info_df["listed_date"] = pd.to_datetime(info_df["listed_date"])
        info_df_list.append(info_df)
    info_df = pd.concat(info_df_list)
    info_df = info_df.drop_duplicates("order_book_id")
    info_df = info_df[info_df["listed_date"]>start_date]
    info_df = info_df[info_df["underlying_symbol"].isin(need_l)]
    info_df["listed_date"] = info_df["listed_date"].dt.strftime("%Y.%m.%d")
    info_df["de_listed_date"] = info_df["de_listed_date"].dt.strftime("%Y.%m.%d")
    print(f"共计{len(info_df)}条待更新")
    print("开始下载k线")
    # with multiprocessing.Pool(processes = 3) as pool:
    #     adds = pool.map(update_bar,[row for _,row in tqdm(info_df.iterrows())])
    print("开始下载tick")
    with multiprocessing.Pool(processes = 5) as pool:
        adds = pool.map(update_tick,[row for _,row in tqdm(info_df.iterrows())])

    
    # for index,row in tqdm(info_df.iterrows()):
    #     update_bar(row)
        # rqFeed.store_his_bar(storage_path,code,s,e,"d",True)
        # rqFeed.store_his_bar(storage_path,code,s,e,"m1",True)
        # gqFeed.store_his_tick(storage_path,code,s,e,True)


        # all_task.append(executor.submit(rqFeed.store_his_bar,(storage_path,code,s,e,"d",True)))
        # all_task.append(executor.submit(rqFeed.store_his_bar,(storage_path,code,s,e,"1m",True)))
        # all_task.append(executor.submit(gqFeed.store_his_tick,(storage_path,code,s,e,True)))
        
     
    # wait(all_task, return_when=ALL_COMPLETED)