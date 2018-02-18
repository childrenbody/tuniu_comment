# -*- coding: utf-8 -*-
from tools import tuniu_db, reptile


# =============================================================================
# pid = 210148605
# db = tuniu_db('localhost', 'root', 'lufei', 'temp')
# db.pid(pid)
# rt = reptile(pid)
# rt.totalPages()
# error = []
# if not db.table_exist(pid):
#     info = rt.info_data()
#     db.insert(info, True)
#     db.create_table()
#     while rt.page <= rt.pages:
#         data = rt.snatch()
#         if db.insert(data):
#             print('page {}/{} ok'.format(rt.page, rt.pages))
#         else:
#             print('page {}/{} is mistake'.format(rt.page, rt.pages))
#             error.append(rt.page)    
#         rt.page += 1
# else:
#     print('product {} already exists')
# =============================================================================





#==============================================================================
#评论分析 
#==============================================================================
import jieba
from jieba.analyse import set_stop_words
from jieba.analyse import extract_tags
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#导入停用词表
set_stop_words('stop.txt')

pid = raw_input(u'请输入产品ID号：')


data , title1, title2= getDatabyID(pid)
if title1 == title2:
    title2 = None
'''
数据如需保存，用下列代码
data.to_csv('data/data.csv',header=False, index=False, encoding='utf-8')
with open('data/title.txt', 'w') as f:
    f.write(title1.encode('utf-8'))

从本地加载数据
with open('data/title.txt', 'r') as f:
   title = f.readline()
data = pd.read_csv('data/data.csv', header=None) 
'''

#对所有用户评论进行分词
text = ' '.join(list(data[0]))

#用来正常显示中文标签
plt.rcParams['font.sans-serif']=['SimHei'] 
#用来正常显示负号
plt.rcParams['axes.unicode_minus']=False   


#用户评论分词
cont_tag = jieba.cut(text)
tags = ' '.join(cont_tag)

#生成词云
wordcloud = WordCloud(font_path="C:/Windows/Fonts/msyh.ttf", background_color="white").generate(tags)
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

#关键词提取
text_tags = extract_tags(text, topK=20, withWeight=True)
data_tags = pd.DataFrame(text_tags, columns=['word', 'weight'])
#绘制关键词直方图
data_tags.plot(x=['word'], kind='barh')

#提取产品关注点，产品标题包含所有该产品的亮点
#返回关键词与权重的dataframe
def title(title):
    title_tag = jieba.cut(title)
    title_set = set(title_tag)
    
    temp = extract_tags(text, topK=1000, withWeight=True)
    text_tag = []
    for w in temp:
        if w[0] in title_set:
            text_tag.append(w)
    
    data_tag = pd.DataFrame(text_tag, columns=['word', 'weight'])
    data_tag.plot(x=['word'], kind='barh')
    return data_tag

#画饼图
def plotData(data_tag):    
    rw = 0.0
    weight = sum(data_tag.weight)
    rw = sum(data_tag.weight[5:])
    
    labels = list(data_tag.word[:5])
    labels.append(u'其他')
    sizes = [j * 100.0 /weight for j in data_tag.weight[:5]]
    sizes.append(rw * 100.0 / weight)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

#获取所有提到产品关注点的用户的id
def comment(data, data_tag):
    words = list(data_tag.word[:5])
    wordList = [list(seq) for seq in data[0].apply(jieba.cut)]
    wordDict = {}
    for j in range(5):
        wList = []
        for i in range(len(wordList)):
            if words[j] in wordList[i]:
                wList.append(i)    
        wordDict[words[j]] = wList
    return wordDict
#统计筛选出的用户的评分
def feeling(data, wordDict):
    feeling = {}
    for word in wordDict.keys():
        wordfeeling = {}
        for feelID in range(1, 5):
            fList = []
            for userID in wordDict[word]:
                fList.append(data.iloc[userID, feelID])
            wordfeeling[feelID] = sum(fList) / float(len(fList))
        feeling[word] = wordfeeling
    print("feeling analyse successfully")
    return feeling

#对情感分析画图
def showfeeling(feeling):
    for i in range(len(feeling)):
        plt.subplot(321+i)
        word = feeling.keys()[i]
        keylist = [u'导游', u'安排', u'住宿', u'交通']
        plt.bar(feeling[word].keys(), feeling[word].values(), width=0.4)
        plt.legend((word,))
        plt.xticks(feeling[word].keys(), keylist)
        plt.ylim(2, 3)
    plt.show()
       
data_tag1 = title(title1)
wordDict = comment(data, data_tag1)
feeling = feeling(data, wordDict)
showfeeling(feeling)
plotData(data_tag1)
if title2:
    data_tag2 = title(title2)
    plotData(data_tag2)
    
