#!/usr/bin/python3

import os
from bs4 import BeautifulSoup
import pymysql
import re
import copy
import json
from datetime import datetime


ctLists = []
#fileExt = '.html'
fileExt = '.jsp'


def dbConnect():
    db_host = '13.209.212.236'
    db_port = 13306
    db_user = 'db-cloudz'
    db_pwd = 'cloudz2021!'
    db_database = 'cloudz'

    # Open database connection
    db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pwd, db=db_database, charset='utf8', autocommit=True)

    return db


def dbClose(db):
    db.close()


def SaveDB():
    db = dbConnect()
    cursor = db.cursor()

    cursor.execute("select * from search_keyword")
    resultList = cursor.fetchall()

    result = list(resultList)

    kwdList = []

    for r in result:
        rList = list(r)
        kwd = rList[1]
        pair = rList[2]

        sql = """select title from search_test where title like %s or contents like %s"""
        num = cursor.execute(sql, (('%' + kwd + '%', '%' + kwd + '%', )))

        if num == 0 and pair == "":
            print("%s   %s  %s" % (kwd, num, pair))
            kwdList.append(kwd)

    print(kwdList)

    dbClose(db)

SaveDB()
print("------------------------------------------------------------------------------------")

