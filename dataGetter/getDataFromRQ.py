from wtpy.apps.datahelper.DHRqData import DHRqData
from wtpy.apps.datahelper import DHFactory as DHF
from wtpy.wrapper.WtDtHelper import WtDataHelper
import datetime as dt
import rqdatac as rq

hlper = DHRqData()

hlper.auth()

# 将代码列表下载到文件中
hlper.dmpCodeListToFile(filename = 'codes.json', hasStock = True, hasIndex = True)

l = ['SHFE.AL', 'SHFE.CU', 'SHFE.RU', 'DCE.M', 'DCE.A', 'CZCE.CF', 'DCE.C', 'CZCE.SR', 'DCE.Y',
                     'CZCE.TA',
                     'SHFE.ZN', 'CZCE.OI', 'DCE.L', 'DCE.P', 'SHFE.RB', 'CZCE.MA', 'CZCE.RM', 'DCE.I', 'DCE.PP',
                     'SHFE.NI']

for comm in l:
    

# 将K线下载到指定目录
hlper.dmpBarsToFile("./", codes = ["SHFE.cu.2202",'SHFE.cu.HOT'], period="min1",start_date=dt.datetime(2021,1,1))

#tick数据的下载暂时只有cpp的模块，python的还没有实现