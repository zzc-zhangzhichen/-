#encoding :utf-8
#读取并输出列表
import csv
import os
file = open(r'C:\Users\86183\Desktop\pythonProject\放射网.csv', encoding='utf-8')
reader = csv.reader(file)
print(list(reader))




#读取并输出元祖
import pandas as pd
df = pd.read_csv('放射网.csv')#因为没有表头，不把第一行作为每一列的索引
data = []
for i in df.index:
    data.append(tuple(df.values[i]))
allnodes = tuple(data)#若想用二维列表的形式读取即删掉此行语句
print(allnodes)


