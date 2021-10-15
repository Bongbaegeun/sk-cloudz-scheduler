#!/usr/bin/python3

import pymysql
import json


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
    filePath = '/home/ec2-user/scheduler/keyword_data.json'
    f = open(filePath, 'r')
    r = f.read()

    read = json.loads(r)

    f.close()
    
    db = dbConnect()
    cursor = db.cursor()

    if len(read) > 0:
        in_sql = "insert into search_keyword (keyword_txt, pair_code) values(%(keyword)s, %(pair_code)s)"

        cursor.executemany(in_sql, read)
        db.commit()
        print("insert data Success")

    dbClose(db)


SaveDB()
print("------------------------------------------------------------------------------------")

