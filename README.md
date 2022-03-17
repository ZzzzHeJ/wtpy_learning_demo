# Python Demos

Python下的demo主要演示不同环境下不同组件的使用<br
提供了一个示例策略，DualThrust，股票和期货都用这个策略

+ cta_fut           期货CTA实盘demo，配置的是SIMNOW通道
+ cta_fut_bt        期货回测demo
+ dataFeed          数据源demo，用来从米筐或者Gqdb获取回测用的历史数据
+ cta_optimizer     CTA策略优化器demo
+ =============================================
+ cta_arbitrage_bt  期货套利回测demo
+ cta_stk           股票CTA实盘demo，配置的是XTP的仿真通道
+ cta_stk_bt        股票回测demo
+ ctp_loader        合约加载器demo
+ datakit_fut       期货数据组件demo
+ datakit_stk       股票数据组件demo
+ hft_fut           期货高频实盘demo
+ hft_fut_bt        期货高频回测demo
+ hft_fut_mocker    期货高频本地仿真demo
+ sel_fut_bt        期货SEL引擎回测demo
+ test_dataexts     数据扩展模块demo
+ test_datahelper   数据辅助模块demo
+ test_extmodules   python外接行情和执行模块demo
+ test_hotpicker    WtHotPicker的用法示例
+ test_monitor      WtMonSvr的用法示例
+ cta_unit_test  CTA策略接口的单元测试demo

# 如何使用这些demo
+ 首先确认本地安装的是 *Python3.6* 以上的版本，32位、64位都可以，wtpy子框架会根据Python的版本自动选择对应的底层
+ 然后安装*WonderTrader*上的*Python*子框架[***wtpy***](https://pypi.org/project/wtpy/)(version = v0.3.2)

```cmd
pip install wtpy
```

## 如何运行回测demo
配置*config.yaml*文件，设置策略参数以及回测设置
```yaml
replayer:
    basefiles:
        commodity: ../common/commodities.json
        contract: ../common/contracts.json
        holiday: ../common/holidays.json
        session: ../common/sessions.json
        hot: ../common/hots.json
    mode: csv
    tick: false  # 是否使用tick回测，如果使用tick需要将mode改为bin
    store:
      module: WtDataStorage
      path: ../storage/
    etime: 201912011500
    stime: 201909010900
    fees: ../common/fees.json
env:
    mocker: cta
```

运行目录下的 *run.py* 即可

如果缺少数据，可以使用*dataFeed*继续宁下载，具体请看dataFeed.py，目前支持米筐与GQDB

## 如何运行实盘demo
### 1. 运行数据组件（datakit_fut）

修改配置文件mdparsers.yaml中的解析器配置。以 *simnow* 通道为例，将********改成自己的simnow账号，然后修改*code*字段为自己要订阅的合约，合约代码规则为"市场代码.合约代码"

```yaml
parsers:
-   active: true
    broker: '9999'
    code: ''
    front: tcp://180.168.146.187:10211
    id: parser
    module: ParserCTP
    pass: 你的SIMNOW密码
    user: 你的SIMNOW账号
```

修改数据dtcfg.yaml中落地模块配置即接受的行情数据存储到哪里

``` yaml
writer:
    async: true                     # 是否异步，异步会把数据提交到缓存队列，然后由独立线程进行处理
    groupsize: 100                  # 每处理这么多条数据就输出一次日志
    path: ../../storage/            # 存储路径
    savelog: true                   # 是否同时输出日志

```

修改dtcfg.yaml中的udp广播配置（目前只开放了内存块直接广播），即数据如何分发给各个策略

```yaml
broadcaster:
    active: true
    bport: 3997
    broadcast:
    -   host: 255.255.255.255
        port: 9001
        type: 2
    multicast_:
    -   host: 224.169.169.169
        port: 9002
        sendport: 8997
        type: 0
    -   host: 224.169.169.169
        port: 9003
        sendport: 8998
        type: 1
    -   host: 224.169.169.169
        port: 9004
        sendport: 8999
        type: 2
```

最后**运行**runDT.py启动行情接受器。

### 2. 运行策略组

首先，修改实盘demo的配置文件*config.yaml*, 再运行实盘demo下的 *run.py*

将数据读取配置中的路径修改为数据组件里配置的路径(config.yaml)

```yaml
data:
    store:
        module: WtDataStorage   #模块名
        path: ../storage/      #数据存储根目录
```

设置交易环境也就是策略的的配置
```yaml
#环境配置
env:
    name: cta               #引擎名称：cta/hft/sel
    product:
        session: TRADING    #驱动交易时间模板，TRADING是一个覆盖国内全部交易品种的最大的交易时间模板，从夜盘21点到凌晨1点，再到第二天15:15，详见sessions.json
    riskmon:                #组合风控设置
        active: true            #是否开启
        module: WtRiskMonFact   #风控模块名，会根据平台自动补齐模块前缀和后缀
        name: SimpleRiskMon     #风控策略名，会自动创建对应的风控策略
        #以下为风控指标参数，该风控策略的主要逻辑就是日内和多日的跟踪止损风控，如果回撤超过阈值，则降低仓位
        base_amount: 5000000    #组合基础资金，WonderTrader只记录资金的增量，基础资金是用来模拟组合的基本资金用的，和增量相加得到动态权益
        basic_ratio: 101        #日内高点百分比，即当日最高动态权益是上一次的101%才会触发跟踪侄止损
        calc_span: 5            #计算时间间隔，单位s
        inner_day_active: true  #日内跟踪止损是否启用
        inner_day_fd: 20.0      #日内跟踪止损阈值，即如果收益率从高点回撤20%，则触发风控
        multi_day_active: false #多日跟踪止损是否启用
        multi_day_fd: 60.0      #多日跟踪止损阈值
        risk_scale: 0.3         #风控系数，即组合给执行器的目标仓位，是组合理论仓位的0.3倍，即真实仓位是三成仓
        risk_span: 30           #风控触发时间间隔，单位s。因为风控计算很频繁，如果已经触发风控，不需要每次重算都输出风控日志，加一个时间间隔，友好一些
fees: ../common/fees.json   #佣金配置文件
executers: executers.yaml   #执行器配置文件
filters: filters.yaml       #过滤器配置文件，这个主要是用于盘中不停机干预的
parsers: tdparsers.yaml     #行情通达配置文件
traders: tdtraders.yaml     #交易通道配置文件
bspolicy: actpolicy.yaml    #开平策略配置文件
```


修改行情通道中的接收端口和接收地址(tdparsers.yaml)

```yaml
parsers:
-   active: true
    bport: 9001
    filter: ''
    host: 127.0.0.1
    id: parser1
    module: ParserUDP
    sport: 3997

```

修改交易通道的配置(tdtraders.yaml)

```yaml
traders:
-   active: true
    appid: simnow_client_test
    authcode: '0000000000000000'
    broker: '9999'
    front: tcp://180.168.146.187:10201
    id: simnow
    module: TraderCTP
    user: "你的SIMNOW账号"
    pass: "你的SIMNOW密码"
    quick: true
    riskmon:
        active: true
        policy:
            default:
                cancel_stat_timespan: 10    # 撤单流量检查间隔
                cancel_times_boundary: 20   # 在间隔中最多的撤单次数
                cancel_total_limits: 470    # 交易日内最多撤单次数
                order_stat_timespan: 10     # 发单流量检查间隔
                order_times_boundary: 20    # 在间隔中最多的发单次数
```

修改执行器的配置，可以根据需要配置多个执行器，执行器和交易通道一对一绑定（executers.yaml)

```yaml
#一个组合可以配置多个执行器，所以executers是一个list
executers:
-   active: true    #是否启用
    id: exec        #执行器id，不可重复
    trader: simnow  #执行器绑定的交易通道id，如果不存在，无法执行
    scale: 1        #数量放大倍数，即该执行器的目标仓位，是组合理论目标仓位的多少倍，可以为小数 

    policy:         #执行单元分配策略，系统根据该策略创建对一个的执行单元
        default:    #默认策略，根据品种ID设置，如SHFE.rb，如果没有针对品种设置，则使用默认策略
            name: WtExeFact.WtMinImpactExeUnit, #执行单元名称
            offset: 0,      #委托价偏移跳数
            expire: 5,      #订单超时没秒数
            pricemode: 1,   #基础价格模式，-1-己方最优，0-最新价，1-对手价
            span: 500,      #下单时间间隔（tick驱动的）
            byrate: false,  #是否按对手盘挂单量的比例挂单，配合rate使用
            lots: 1,        #固定数量
            rate: 0         #挂单比例，配合byrate使用

    clear:                  #过期主力自动清理配置
        active: false       #是否启用
        excludes:           #排除列表
        - CFFEX.IF
        - CFFEX.IC
        includes:           #包含列表
        - SHFE.rb
```

修改自动开平策略的配置文件*actpolicy.yaml*
以股指为例，股指平今手续费很高，所以开平优先级顺序为：平昨开仓平今
如果是上期黄金和白银等品种，平今为0，则优先级顺序为：平今平昨开仓
```yaml
default:                #默认开平策略：先平仓，再开仓
    order:              #顺序
    -   action: close   #开平动作：open-开仓，close-平仓，closetoday-平今，closeyestoday-平昨
        limit: 0        #限手，0为不限制
    -   action: open    
        limit: 0
#低日内佣金策略：平今>平昨>开仓
lowinnerdayfee:
    filters:            #品种过滤器，如果设定了该项，则这些品种就使用该策略
    - DCE.a
    - DCE.cs
    - DCE.i
    - DCE.j
    - DCE.l
    - DCE.m
    - DCE.p
    - DCE.pp
    - SHFE.au
    - SHFE.hc
    - CZCE.ZC
    - CZCE.CF
    - CZCE.MA
    - CZCE.SR
    - CZCE.AP
    order:
    -   action: closetoday
        limit: 0
    -   action: closeyestoday
        limit: 0
    -   action: open
        limit: 0
        
#股指开平策略：平昨>开仓>平今，开仓有限手500
#如果是买入，先看是否有昨日空头，再开多仓，如果多仓已经打到限手，再平当日的空头
stockindex:
    filters:
    - CFFEX.IF
    - CFFEX.IC
    - CFFEX.IH
    order:
    -   action: closeyestoday
        limit: 0
    -   action: open
        limit: 500
    -   action: closetoday
        limit: 0

```