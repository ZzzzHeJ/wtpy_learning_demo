from wtpy.wrapper import WtDataHelper

if __name__ == '__main__':
    dtHelper = WtDataHelper()
    dtHelper.dump_bars(binFolder="./bin/day", csvFolder="./csv/day")
    dtHelper.dump_bars(binFolder="./bin/min1", csvFolder="./csv/min1")
    dtHelper.dump_ticks(binFolder="./bin/ticks", csvFolder="./csv/ticks")