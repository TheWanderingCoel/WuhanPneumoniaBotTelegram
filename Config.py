import sys
from configobj import ConfigObj

config = ConfigObj(sys.path[0] + "/Conf/General.conf", encoding="UTF8")