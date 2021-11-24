__author__ = "seraph92@gmail.com"
# Logging Module

import sys
import datetime
import logging
import logging.handlers

from Config import CONFIG

LOG = logging.getLogger()

# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0


if CONFIG['logging'] == "INFO":
    LOG.setLevel(logging.INFO)
elif CONFIG['logging'] == "DEBUG":
    LOG.setLevel(logging.DEBUG)
elif CONFIG['logging'] == "ERROR":
    LOG.setLevel(logging.ERROR)
elif CONFIG['logging'] == "CRITICAL":  # CRITICAL == FATAL
    LOG.setLevel(logging.CRITICAL)
elif CONFIG['logging'] == "FATAL":
    LOG.setLevel(logging.FATAL)
elif CONFIG['logging'] == "WARN": # WARN == WARNING
    LOG.setLevel(logging.WARN)
elif CONFIG['logging'] == "WARNING":
    LOG.setLevel(logging.WARNING)
elif CONFIG['logging'] == "NOTSET":
    LOG.setLevel(logging.NOTSET)
else:
    LOG.setLevel(logging.ERROR)

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

file_handler = logging.FileHandler(f"./log/scrap_{formattedDate}.log", encoding='utf-8')
file_handler.setFormatter(formatter)
LOG.addHandler(file_handler)

timed_file_handler = logging.handlers.TimedRotatingFileHandler(filename=f"./log/scrap_log", when='midnight', interval=1, encoding='utf-8')
timed_file_handler.setFormatter(formatter)
LOG.addHandler(timed_file_handler)