from wtpy.monitor import WtMonSvr
import sys
import os
os.chdir(sys.path[0])
svr = WtMonSvr(deploy_dir="./deploy")
svr.run(port=8099, bSync=False)
input("press enter key to exit\n")