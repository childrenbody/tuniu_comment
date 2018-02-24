#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 23:21:53 2018

@author: childrenbody
"""
import requests, pymysql, datetime
from jieba.analyse import set_stop_words, extract_tags
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['simhei']    # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

class Tuniu_db:
    """
    database's class of tuniu, 
    initialization parameters: host, user, password, db=tuniu_db
    """
    def __init__(self, host, user, password, db='tuniu_db'):
        self.conn = pymysql.connect(host, user, password, db, charset='utf8')

    def close(self): self.conn.close()
    
    def table(self, productId): 
        self.pid = str(productId)
        self.table = "product_{}".format(self.pid)
        
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
            table = self.table if not info else 'product_info'
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
        sql = """create table {}
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
                 );""".format(self.table)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
        self.conn.commit()

    def clear(self):
        """
        delete rows in product_info and drop table product_id by product id
        """
        delete = "DELETE FROM product_info WHERE productId = {}".format(self.pid)
        drop = "DROP TABLE {}".format(self.table)
        with self.conn.cursor() as cursor:
            cursor.execute(delete)
            cursor.execute(drop)
        self.conn.commit()

    def select_pd(self, *args, nrows=None):
        """
        Select all rows from table, args will get column's name, return dataframe
        """
        nrows = "limit {}".format(str(nrows)) if nrows else ""
        sql = "select {0} from {1} {2};".format(",".join(args), self.table, nrows)
        return pd.read_sql(sql, self.conn)

    def select_all(self, *args):
        """
        Select all rows and that return data
        """
        sql = "SELECT {0} from {1};".format(",".join(args) , self.table)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

class Reptile:
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
    
class Analysis:
    def __init__(self):
        set_stop_words('stop.txt')
        
    def import_plt():
        """
        import plt and set chinese font
        """
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif']=['SimHei']    # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

    
    def get_data(self, data): self.data = data
    
    def comments_month(self):
        """
        Show the quantity of comments basis month, need remarkTime
        """
        self.data['comments_month'] = self.data.remarkTime.apply(lambda x: x.strftime("%Y-%m"))
        temp = self.data.groupby(by='comments_month')['remarkTime'].count()
        self.data.drop('comments_month', axis=1, inplace=True)
        temp.plot() 
        
    def get_text(self, data: "get data from tuniu_db"):
        """
        get all comment's content, first get data from tuniu_db
        """
        data = [c[0] for c in data]
        return " ".join(data)

    def key_word(self, data, k=20):
        text = self.get_text(data)
        text_tags = extract_tags(text, topK=k, withWeight=True)
        data_tags = pd.DataFrame(text_tags, columns=['word', 'weight'])
        data_tags.plot(x=['word'], kind='barh')
        return data_tags
        
if __name__ == '__main__':
    pid = 210148605
    db = Tuniu_db('localhost', 'root', 'lufei', 'temp')
    db.table(pid)
    data = db.select_all('compTextContent')
    al = Analysis()
    Analysis.import_plt()
    data = al.key_word(data)

   


