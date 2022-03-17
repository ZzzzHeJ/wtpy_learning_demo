from dataFeed import RqFeed
feed = RqFeed()
import datetime as dt

update_list = [
    "SHFE.al.2204","SHFE.al.2205","SHFE.cu.2204","SHFE.cu.2205","SHFE.ru.2205","SHFE.ru.2209","DCE.m.2205","DCE.m.2209","DCE.a.2207","DCE.a.2205","CZCE.CF.2205","CZCE.CF.2209","DCE.c.2205","DCE.c.2209","CZCE.SR.2205","CZCE.SR.2209","DCE.y.2205","DCE.y.2209","CZCE.TA.2205","CZCE.TA.2206","SHFE.zn.2204","SHFE.zn.2205","CZCE.OI.2205","CZCE.OI.2207","DCE.l.2205","DCE.l.2206","DCE.p.2205","DCE.p.2209","SHFE.rb.2205","SHFE.rb.2210","CZCE.MA.2205","CZCE.MA.2206","CZCE.RM.2205","CZCE.RM.2207","DCE.i.2205","DCE.i.2209","DCE.pp.2205","DCE.pp.2206","SHFE.ni.2204","SHFE.ni.2205"
]
storage_path = r"\\WIN-52AMQLH0TIA\WonderTrader\storage"
for symbol in update_list: 
    feed.store_his_bar(storage_path,symbol,"2022.1.1",dt.datetime.now().strftime("%Y.%m.%d"),"d",False)