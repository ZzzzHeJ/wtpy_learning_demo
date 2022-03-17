from ctypes import cdll,c_char_p
from wtpy.wrapper import WtDataHelper

if __name__ == '__main__':
    api = cdll.LoadLibrary("DataTools.dll")
    api.tick_bin2csv("./bin","test")