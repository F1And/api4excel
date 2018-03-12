# api4excel - 接口自动化测试excel篇

####  工作原理: 测试用例在excel上编辑，使用第三方库xlrd，读取表格sheet和内容，sheetName对应模块名，Jenkins集成服务发现服务moduleName查找对应表单，运用第三方库requests请求接口，根据结果和期望值进行断言，根据输出报告判断接口测试是否通过。

###### 1. 数据准备
 - 数据插入（容易实现的测试场景下所需外部数据)
 - 准备sql （接口需要重复使用，参数一定得是变量)

###### 2.集成部署(运维相关了解即可)
- 平滑升级验证脚本加入自动化

###### 3.自动化框架实现
- 调用mysql
- excel遍历测试用例
- requests实现接口调用
- 根据接口返回的code值和Excel对比
- 报告反馈
- 暴露服务

**写一个简单登录的接口自动化测试**

##### 代码的分层如下图：

 ![代码结构](https://upload-images.jianshu.io/upload_images/2955280-61684f7211311214.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


#### 一、写一个封装的获取excel表格的模块 ####


![excel.png](http://upload-images.jianshu.io/upload_images/2955280-932a018763266a33.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


代码实现如下：
``` python
 # !/usr/bin/python
 # -*- coding: UTF-8 -*-
 # author: 赫本z
 # 基础包: excel的封装

import xlrd
workbook = None

def open_excel(path):
     """
     打开excel
     :param path: 打开excel文件的位置
     """
     global workbook
     if (workbook == None):
        workbook = xlrd.open_workbook(path, on_demand=True)

def get_sheet(sheetName):
     """
     获取页名
     :param sheetName: 页名
     :return: workbook
     """
     global workbook
     return workbook.sheet_by_name(sheetName)

def get_rows(sheet):
    """
    获取行号
    :param sheet: sheet
    :return: 行数
    """
    return sheet.nrows

def get_content(sheet, row, col):
    """
    获取表格中内容
    :param sheet: sheet
    :param row: 行
    :param col: 列
    :return:
    """
    return sheet.cell(row, col).value

def release(path):
    """释放excel减少内存"""
    global workbook
    workbook.release_resources()
    del workbook
    # todo:没有验证是否可用

```

   代码封装后当成模块引用，这还是最开始呢。

#### 二、引用log模块获取日志 ####

准备工作：
需要一个日志的捕获，包括框架和源码抛出的expection。
代码如下：
``` python
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
```

#### 三、引用requests模块接口测试 ####

准备工作：
需要的请求类型和执行测试的方法。
代码如下：

``` python
#!/usr/bin/python
#-*- coding: UTF-8 -*-
# 基础包：接口测试的封装

import requests
import core.log as log
import json

logging = log.get_logger()

def change_type(value):
    """
    对dict类型进行中文识别
    :param value: 传的数据值
    :return: 转码后的值
    """
    try:
        if isinstance(eval(value), str):
            return value
        if isinstance(eval(value), dict):
            result = eval(json.dumps(value))
            return result
    except Exception, e:
        logging.error("类型问题 %s", e)


def api(method, url, data ,headers):
    """
    自定义一个接口测试的方法
    :param method: 请求类型
    :param url: 地址
    :param data: 数据
    :param headers: 请求头
    :return: code码
    """
    global results
    try:
        if method == ("post" or "POST"):
            results = requests.post(url, data, headers=headers)
        if method == ("get" or "GET"):
            results = requests.get(url, data, headers=headers)
      # if method == "put":
      #     results = requests.put(url, data, headers=headers)
      # if method == "delete":
      #     results = requests.delete(url, headers=headers)
      # if method == "patch":
      #     results == requests.patch(url, data, headers=headers)
      # if method == "options":
      #     results == requests.options(url, headers=headers)
        response = results.json()
        code = response.get("code")
        return code
    except Exception, e:
        logging.error("service is error", e)


def content(method, url, data, headers):
    """
    请求response自己可以自定义检查结果
    :param method: 请求类型
    :param url: 请求地址
    :param data: 请求参数
    :param headers: 请求headers
    :return: message信息
    """
    global results
    try:
        if method == ("post" or "POST"):
            results = requests.post(url, data, headers=headers)
        if method == ("get" or "GET"):
            results = requests.get(url, data, headers=headers)
        if method == ("put" or "PUT"):
            results = requests.put(url, data, headers=headers)
        if method == ("patch" or "PATCH"):
            results = requests.patch(url, data, headers=headers)
        response = results.json()
        message = response.get("message")
        result = response.get("result")
        content = {"message": message, "result": result}
        return content
    except Exception, e:
        logging.error("请求失败 %s" % e)

```

#### 四、关于function模块 ####
  主要调用二次封装的代码，结合业务做一个通用代码。如下：

``` python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 业务包：通用函数


import core.mysql as mysql
import core.log as log
import core.request as request
import core.excel as excel
import constants as cs
from prettytable import PrettyTable

logging = log.get_logger()


class ApiTest:
    """接口测试业务类"""
    filename = cs.FILE_NAME

    def __init__(self):
        pass

    def prepare_data(self, host, user, password, db, sql):
        """数据准备，添加测试数据"""
        mysql.connect(host, user, password, db)
        res = mysql.execute(sql)
        mysql.close()
        logging.info("Run sql: the row number affected is %s", res)
        return res

    def get_excel_sheet(self, path, module):
        """依据模块名获取sheet"""
        excel.open_excel(path)
        return excel.get_sheet(module)

    def get_prepare_sql(self, sheet):
        """获取预执行SQL"""
        return excel.get_content(sheet, cs.SQL_ROW, cs.SQL_COL)

    def run_test(self, sheet, url):
        """再执行测试用例"""
        rows = excel.get_rows(sheet)
        fail = 0
        for i in range(2, rows):
            testNumber = str(int(excel.get_content(sheet, i, cs.CASE_NUMBER)))
            testData = excel.get_content(sheet, i, cs.CASE_DATA)
            testName = excel.get_content(sheet, i, cs.CASE_NAME)
            testUrl = excel.get_content(sheet, i, cs.CASE_URL)
            testUrl = url + testUrl
            testMethod = excel.get_content(sheet, i, cs.CASE_METHOD)
            testHeaders = eval(excel.get_content(sheet, i, cs.CASE_HEADERS))
            testCode = excel.get_content(sheet, i, cs.CASE_CODE)
            actualCode = request.api(testMethod, testUrl, testData, testHeaders)
            expectCode = str(int(testCode))
            failResults = PrettyTable(["Number", "Method", "Url", "Data", "ActualCode", "ExpectCode"])
            failResults.align["Number"] = "l"
            failResults.padding_width = 1
            failResults.add_row([testNumber, testMethod, testUrl, testData, actualCode, expectCode])

            if actualCode != expectCode:
                logging.info("FailCase %s", testName)
                print "FailureInfo"
                print failResults
                fail += 1
            else:
                logging.info("Number %s", testNumber)
                logging.info("TrueCase %s", testName)
        if fail > 0:
            return False
        return True
```

#### 五、关于参数中constans模块 ####

准备工作：
所有的参数和常量我们会整理到这个文件中，因为设计业务和服务密码、数据库密码这里展示一部分。
代码如下：

``` python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 通用包：常量

CASE_NUMBER = 0  # 用例编号
CASE_NAME = 1    # 用例名称
CASE_DATA = 2    # 用例参数
CASE_URL = 3     # 用例接口地址
CASE_METHOD = 4  # 用例请求类型
CASE_CODE = 5    # 用例code
CASE_HEADERS = 6 # 用例headers

SQL_ROW = 0      # 预执行SQL的行号
SQL_COL = 1      # 预执行SQL的列号

FILE_NAME = 'test.xlsx'
```

#### 六、写一个run文件：只是用来执行的，业务和代码剥离。 ####

代码如下：
``` python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

```


#### 七、查看测试报告（部署到jenkins会通过控制台查看） ####


![报告.png](http://upload-images.jianshu.io/upload_images/2955280-59a60c84bc40b3b5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
