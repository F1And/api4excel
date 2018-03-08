#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author: 赫本z
# 基础包: 日志服务
import logging

def get_logger():
    global logPath
    try:
        logPath
    except NameError:
        logPath = ""
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    return logging