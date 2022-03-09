from wtpy import WtEngine,EngineType
from Strategies.DualThrust import StraDualThrust

from ConsoleIdxWriter import ConsoleIdxWriter

if __name__ == "__main__":
    #创建一个运行环境，并加入策略
    env = WtEngine(EngineType.ET_CTA)
    env.init('../common/', "config.json")
    
    # 添加策略
    straInfo1 = StraDualThrust(name='Strategy1', code="SHFE.au.HOT", barCnt=50, period="m1", days=30, k1=0.2, k2=0.2, isForStk=False)
    straInfo2 = StraDualThrust(name='Strategy2', code="SHFE.au.HOT", barCnt=50, period="m5", days=30, k1=0.6, k2=0.8, isForStk=False)
    env.add_cta_strategy(straInfo1)
    env.add_cta_strategy(straInfo2)
    
    idxWriter = ConsoleIdxWriter()
    env.set_writer(idxWriter)

    env.run()

    kw = input('press any key to exit\n')