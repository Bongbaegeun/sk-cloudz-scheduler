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


def get_url(dirname, filename):
    #url = 'https://www.cloudz.com/'
    url = '/'
    urlPath = ''

    filename = filename.replace(dirname, '').replace('views', '')
    file_copy = copy.deepcopy(filename).split('/')

    if len(file_copy) > 1:
        if filename.find('index.jsp') >= 0:
            urlPath = filename.replace('index.jsp', '')
        else:
            urlPath = filename.replace(fileExt, '')
    else:
        if filename.find('index.jsp') >= 0:
            urlPath = ''
        else:
            urlPath = filename.replace(fileExt, '')

    #print(url + urlPath)

    return url + urlPath


def rm_tag(c):
    c.lstrip().rstrip()
    #c.replace('\\n', '')
    #c.replace('\\t', '')
    new_string = re.sub(r'\n', ' ', c)
    new_string = re.sub(r'  ', '', new_string)
    new_string = re.sub(r'\t', '', new_string).rstrip().lstrip()

    return new_string


def get_title(service, bs):
    print('service = %s' %str(service))

    reTitle = ""

    if service == 'support':
        header = bs.find('div', class_='notice-header')

        if header != None:
            title = header.find('h3')
            if header.h3 != None:
                reTitle = rm_tag(header.h3.get_text())
    else:
        header = bs.find('header', class_='sub-header')

        if header != None:
            title = header.find('div', class_='inner-wrap')
            if title != None:
                if title.h2 != None:
                    reTitle = rm_tag(title.h2.get_text())

    return reTitle


def get_desc(service, bs):
    reTitle = ""

    if service == 'support':
        body = bs.find('div', class_='notice-body')

        if body != None:
            reTitle = rm_tag(body.get_text())
    else:
        header = bs.find('header', class_='sub-header')

        if header != None:
            title = header.find('div', class_='inner-wrap')
            if title != None:
                if title.p != None:
                    reTitle = rm_tag(title.p.get_text())
                else:
                    reTitle = get_desc2(bs)

    return reTitle


def get_desc2(bs):
    reDesc = ''
    body = bs.find('div', class_='entry-content')
    
    if body != None:
        h2 = ''
        p = ''

        if body.header != None:
            if body.header.h2 != None:
                h2 = body.header.h2.get_text()

            if body.header.p != None:
                p = body.header.p.get_text()

        desc = h2 + p
        reDesc = rm_tag(desc)

    return reDesc


def get_contents(service, bs):
    reContents = ''

    if service == 'partners':
        reContents = '삼양데이터시스템, ㈜유더블유에스, 씨앤토트시스템㈜, ㈜도연시스템즈, ㈜솔박스, ㈜브이시스템즈, 주식회사 에이피솔루션즈, 한국컨텐츠인프라, ㈜웰데이타시스템, ㈜써드아이시스템, 주식회사 미르헨지, 에이블컴㈜, ㈜파루씨앤씨, 인프라소프트㈜, ㈜엠아이티마스, 엔키위, ADT캡스, 퓨처웨어㈜, 코니퍼㈜, ㈜유리시스템, 아이소프트, 동덕정보통신㈜, ㈜솔빛아이텍, ㈜유비벨록스모바일, 코오롱베니트주식회사, ㈜온더아이티, 엘비텍㈜, 인프라닉스㈜, ㈜부뜰정보시스템, ㈜퓨처젠, ㈜비투아시스템즈, 유니원아이앤씨㈜, ㈜에이포유, 그루터기 주식회사, ㈜에이치씨엔씨, ㈜에이에스피엔, ㈜에이텍아이엔에스, 인지테크, ㈜쓰리에이치에스, 웹프라임㈜, ㈜다나테크원, 리눅스데이타시스템, ㈜링네트, 베이넥스, ㈜에이시스, ㈜에즈웰플러스, 인텍앤컴퍼니, 상해아이요넷, 디딤365㈜, ㈜티맥스소프트, 피수닷컴, 펜타시큐리티, 주식회사 피앤피시큐어'
    else:
        body = bs.find('div', class_='entry-content')
        if body != None:
            reContents = rm_tag(body.get_text())

    return reContents


def saveFile(saveJson):
    save_path = '/home/ec2-user/scheduler/searchData.json'
    f = open(save_path, 'w')
    f.write(saveJson)
    f.close()

    print('step 3 : success save json file')


def SaveContents(data):
    ctLists.append(data)


def SaveDB():
    db = dbConnect()
    cursor = db.cursor()

    # truncate search
    cursor.execute("truncate search_test")
    db.commit()
    print("step 1 : truncate table Success!")

    if len(ctLists) > 0:
        in_sql = "insert into search_test (service, title, description, contents, url) values(%(service)s, %(title)s, %(description)s, %(contents)s, %(url)s)"

        cursor.executemany(in_sql, ctLists)
        db.commit()
        print("step 2 : insert data Success")

    dbClose(db)

    # save jaon file
    saveJson = json.dumps(ctLists)
    saveFile(saveJson)


def search(dirname):
    try:
        filepath = '/home/ec2-user/cloudz/apache-tomcat-9.0.50/webapps/ROOT/WEB-INF/views/'
        dirNm = copy.deepcopy(dirname)
        filenames = os.listdir(dirNm)

        for filename in filenames:
            fullPath = os.path.join(dirNm, filename)
            Path_copy = copy.deepcopy(fullPath)

            # pass page : common
            if fullPath.find("/common/") >= 0 or fullPath.find("/customer/") >= 0 or fullPath.find("/customerstory/") >= 0 or fullPath.find("/terms/") >= 0 or fullPath.find("/privacy/") >= 0:
                continue

            if os.path.isdir(fullPath):
                search(fullPath)
            else:
                #print(fullPath)

                ext = os.path.splitext(Path_copy)[-1]
                tmp = Path_copy.replace(filepath, '').replace('views', '').split('/')
                service = None

                if ext != fileExt:
                    continue

                #print("tmp = %s" %str(tmp))

                if len(tmp) < 2:
                    #if fullPath.find("index.html") >= 0:
                    #    continue

                    #service = "main"
                    continue
                else:
                    if fullPath.find("/cloud-marketplace/") >= 0:
                        if fullPath.find("index.jsp") >= 0:
                            continue

                    if fullPath.find("/services/") >= 0:
                        if fullPath.find("index.jsp") >= 0 or fullPath.find("sub.jsp") >= 0:
                            continue

                    if fullPath.find("/support") >= 0:
                        if fullPath.find("index.jsp") >= 0 or fullPath.find("contact-us") >= 0 or fullPath.find("help-desk.jsp") >= 0 or fullPath.find("faq.jsp") >= 0:
                            continue

                    if fullPath.find("/partners") >= 0:
                        if fullPath.find("become.jsp") >= 0:
                            continue

                    if fullPath.find("/about-us") >= 0:
                        if fullPath.find("news.jsp") >= 0:
                            continue

                    service = tmp[0]

                f = open(fullPath, 'r')
                r = f.read()

                bs = BeautifulSoup(r, 'lxml')

                contents = {}
                contents['service'] = service
                contents['title'] = get_title(service, bs)
                contents['description'] = get_desc(service, bs)
                contents['contents'] = get_contents(service, bs)
                contents['url'] = get_url(filepath, fullPath)

                #print(contents)
                #print("\n")
                SaveContents(contents)

                f.close()

        #print(ctLists)

    except Exception as e:
        print("error : " %str(e))
        return -500, str(e)


today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
print("[%s]" % today)
filepath = '/home/ec2-user/cloudz/apache-tomcat-9.0.50/webapps/ROOT/WEB-INF/views/'
search(filepath)
SaveDB()
print("------------------------------------------------------------------------------------")

