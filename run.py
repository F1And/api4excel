#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author: 赫本z
# 验证包：接口测试脚本

import core.log as log
from function.func import ApiTest

func = ApiTest()
logging = log.get_logger()

"""1.外部输入参数"""

module = 'user'
url = 'http://127.0.0.1:8080'

"""2.根据module获取Sheet"""
logging.info("-------------- Execute TestCases ---------------")
sheet = func.get_excel_sheet(func.filename,  module)

# """3.数据准备"""
# logging.info("-------------- Prepare data through MysqlDB --------------")
# sql = func.get_prepare_sql(sheet)
# func.prepare_data(host=host, user=user, password=password, db=db, sql=sql)

"""4.执行测试用例"""
res = func.run_test(sheet, url)
logging.info("-------------- Get the result ------------ %s", res)
