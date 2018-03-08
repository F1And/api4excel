#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author: 赫本z
# 基础包: MySQL

import pymysql.cursors
import core.log as log


logging = log.get_logger()
conn = None

def connect(host, user, password, db, charset='utf8'):
    """
    链接Mysql
    :param host: 地址
    :param user: 用户
    :param password: 密码
    :param db: 数据库名
    :param charset: 数据类型
    :return: 链接
    """
    global conn
    if conn == None:
        conn = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               charset=charset,
                               cursorclass=pymysql.cursors.DictCursor)
    return conn


def execute(sql):
    """
    执行SQL
    :param sql: 执行的SQL
    :return: 影响行数
    """
    global conn
    try:
        with conn.cursor() as cursor:
            res = cursor.execute(sql)
        conn.commit()
        # 这里一定要写commit 不然提交的sql 都会被事务回滚
        return res
    except Exception, e:
        logging.error("sql is empty or error %s" % e)


def close():
    """
    关闭MySQL连接
    :return: None
    """
    global conn
    conn.close()
