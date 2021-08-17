__author__ = "seraph92@gmail.com"
# Logging Module

import sys
import datetime
import logging

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOG.addHandler(stream_handler)

def getCurFuncInfo(depth):
    # sys._getframe().f_lineno
    fName = sys._getframe(depth).f_code.co_name
    lName = sys._getframe(depth).f_lineno
    return ( fName, lName )

def DEBUG(msg):
    #LOG.debug("[" + getCurFuncInfo(2) + "] " + msg)
    LOG.debug("[%s:%d] "%getCurFuncInfo(2) + str(msg))

def ERROR(msg):
    LOG.error("[%s:%d] "%getCurFuncInfo(2) + str(msg))

def INFO(msg):
    LOG.info("[%s:%d] "%getCurFuncInfo(2) + str(msg))

# log file handler
now = datetime.datetime.now()
#formattedDate = now.strftime("%Y%m%d_%H%M%S")
formattedDate = now.strftime("%Y%m%d")
#print(formattedDate)
file_handler = logging.FileHandler(f"./log/scrap_{formattedDate}.log")
file_handler.setFormatter(formatter)
LOG.addHandler(file_handler)