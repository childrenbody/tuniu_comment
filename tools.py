#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 23:21:53 2018

@author: childrenbody
"""
import requests, pymysql, datetime, jieba
from jieba.analyse import set_stop_words, extract_tags

class tuniu_db:
    """
    database's class of tuniu, 
    initialization parameters: host, user, password, db=tuniu_db
    """
    def __init__(self, host, user, password, db='tuniu_db'):
        self.conn = pymysql.connect(host, user, password, db, charset='utf8')

    def close(self): self.conn.close()
    
    def pid(self, productId): self.pid = str(productId)
        
    def table_exist(self, pid):
        with self.conn.cursor() as cursor:        
            sql = "SELECT * FROM product_info WHERE productId = {0}".format(pid)
            result = cursor.execute(sql)
            return True if result else False

    def data_convert(self, data, info=False):
        if not info:
            temp = []
            for r in data:
                temp.append("({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, {10})".format(*r))
            result = ",".join(temp)
        else:
            result = "('{0}', {1}, {2}, '{3}')".format(*data)
        return result


    def insert(self, array, info=False):
        data = self.data_convert(array, info)
        if not info:
            columns = "(custId, custName, remarkTime, productName, productCategoryName, travelType, compTextContent, guideService, itinerary, dining, transport)"
        else:
            columns = "(last_modified, productId, totalItems, productName)"
        try:
            table = "product_{}".format(self.pid) if not info else 'product_info'
            with self.conn.cursor() as cursor:            
                sql = "INSERT INTO {0}{1} VALUES{2};".format(table, columns, data)
                cursor.execute(sql)
        except Exception:
            print('make a progamming error')
            return False
        else:
            self.conn.commit()
            return True
        
    def create_table(self):
        sql = """create table product_{}
                 (
                    id int not null auto_increment,
                    custId char(20) not null,
                    custName char(20),
                    remarkTime datetime not null,
                    productName char(100) not null,
                    productCategoryName char(50),
                    travelType char(10),
                    compTextContent varchar(500) not null,
                    guideService int not null,
                    itinerary int not null,
                    dining int not null,
                    transport int not null,
                    primary key (id)
                 );""".format(self.pid)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
        self.conn.commit()

    def clear(self):
        """
        delete rows in product_info and drop table product_id by product id
        """
        delete = "DELETE FROM product_info WHERE productId = {}".format(self.pid)
        drop = "DROP TABLE product_{}".format(self.pid)
        with self.conn.cursor() as cursor:
            cursor.execute(delete)
            cursor.execute(drop)
        self.conn.commit()

class reptile:
    """
    reptile of tuniu website, last modified: 2018-02-17 21:24:19
    Initialization parameters: proudcutId
    """
    def __init__(self, productId):
        self.pid = productId
        self.page = 1
        
    def status_code(self): return requests.get(self.getUrl()).status_code
    
    def totalPages(self): self.pages = self.getContent()['data']['totalPages']
    
    def now(self): return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def info_data(self):
        contents = self.getContent()['data']
        pName = contents['contents'][0]['productName']
        pName = pName[pName.index('<'): pName.index('>') + 1]
        return [self.now(), self.pid, contents['totalItems'], pName]
    
    def print_status_code(self):
        status = {200:"服务器成功返回网页", 404:"请求的网页不存在", 503:"服务器超时"}
        code = self.status_code()
        print(status[code])
        
    def getUrl(self):
        url = 'http://www.tuniu.com/papi/product/remarkList?productId='+str(self.pid)+'&productType=1&page='+ str(self.page)
        return url
    
    def getContent(self):
        contents = requests.get(self.getUrl()).json()
        assert contents['data']['contents'], 'no contents'
        return contents
    
    def getReview(self): return self.getContent()['data']['contents']
    
    def snatch(self):
        review = self.getReview()
        result = []
        gradeList = ['导游服务', '行程安排', '餐饮住宿', '旅行交通']
        for c in review:
            temp = [c['custId'], c['custName'], c['remarkTime'], c['productName'],
                    c['productCategoryName'], c['travelType']['name'], c['compTextContent']['dataSvalue']]
            grade = [0]*4
            for g in c['subGradeContents']:
                grade[gradeList.index(g['notes'])] = g['dataIvalue']
            temp.extend(grade)
            result.append(temp)
        return result
                
    def fetchAll(self):
        result = []
        self.totalPage()
        while self.page <= self.pages:
            result.extend(self.snatch())
            self.page += 1
        return result
    
class analysis:
    def __init__():
        set_stop_words('stop.txt')
        
    def import_mat():
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif']=['SimHei']
        plt.rcParams['axes.unicode_minus']=False
    
if __name__ == '__main__':
    pid = 210148605
    db = tuniu_db('localhost', 'root', 'lufei', 'temp')
    db.pid(pid)
    rt = reptile(pid)
    rt.page = 15
    data = rt.snatch()
    db.insert(data)
    

   


