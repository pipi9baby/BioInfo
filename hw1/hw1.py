#coding=utf-8
import json
import numpy as np
from tkinter import *
import pickle
import re
from gensim.models import word2vec
from pattern.en import lemma
import gensim
import html
from sklearn import svm

from sklearn.metrics import accuracy_score

#算word to vector
def Content2wv(line):
	pat = re.compile(r'([A-z]+)')
	#分詞
	line = line.replace('\n','')
	words = line.split(" ")
	vector = np.zeros((100, 100), dtype=np.float)
	#算向量
	for i in range(0,len(words)):
		#word = lemma(words[i])
		match = pat.findall(words[i])
		if match:
			try:
				vector += np.array(model.wv[match[0].lower()])
			except:
				try:
					vector += np.array(model.wv[lemma(match[0])])
				except:
					#print(lemma(match[0]))
					vector += np.zeros((100, 100), dtype=np.float)
		else:
			tmp = np.full((100, 100), -1, dtype=float)
			vector += tmp
	#取平均
	tmpLi = []
	for i in range(len(vector)):
		for j in range(len(vector[i])):
			vector[i][j] = vector[i][j]/len(words)
		tmpLi = tmpLi + list(vector[i])
	return tmpLi

#算字元數
def CountCharNum(text):
	pat = re.compile(r'[\S]')
	match = pat.findall(text)
	return len(match)

#找第Ｎ次出現的字串
def find_NthLi(haystack, charLi, start):
	index = haystack.find(charLi[0],start)
	for i in range(1,len(charLi)):
		tmpindex = haystack.find(charLi[i],start)
		if(tmpindex < index and tmpindex != -1):
			index = tmpindex
	return index

#移除html tag
def cleanhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

inputFile = r"/Users/pipi9baby/Desktop/bioInfo/hw1/testData/pubMed/pubmed4.xml"
trainFile = r"/Users/pipi9baby/Desktop/bioInfo/eosModel.pickle"
libraryPath = r"/Users/pipi9baby/Desktop/bioInfo/hw1/corpus/text8.model"
keyword = input("請輸入想搜尋的關鍵字：")
#訓練語料庫
#sentences = word2vec.Text8Corpus(libraryPath)# 加载语料
#model = word2vec.Word2Vec(sentences, size=100)  # 训练skip-gram模型; 默认window=5
#保存model，以便重用
#model.save("text8.model")
#讀model出來
model = word2vec.Word2Vec.load(libraryPath)

fr = open(inputFile)
lemmakey = lemma(keyword)

window = Tk()
printText = Text(window, height=50, width=100)
scroll = Scrollbar(window, command=printText.yview)
printText.configure(yscrollcommand=scroll.set)

text=""
#判斷是json還是xml
if('.xml' in inputFile):
	alltext = fr.read()
	#Title
	pat = re.compile(r"<Title>(.+)</Title>")
	match = pat.findall(alltext)
	title = html.unescape(match[0])
	#abstract
	pat = re.compile(r'<Abstract>[\W](.+)')
	match = pat.findall(alltext)
	abstract = html.unescape(cleanhtml(match[0].strip()))
	text = abstract
	#Author
	pat1 = re.compile(r'<LastName>(.+)</LastName>')
	pat2 = re.compile(r'<ForeName>(.+)</ForeName>')
	match1 = pat1.findall(alltext)
	match2 = pat2.findall(alltext)
	name =[]
	for i in range(len(match1)):
		name.append(match1[i]+" "+match2[i])
	author = ','.join(name)

	#顯示視窗
	printText.tag_configure('bold_italics', font=('Arial', 12, 'bold', 'italic'))
	printText.tag_configure('big', font=('Verdana', 20, 'bold'))
	printText.tag_configure('tikeyword', background='#FFFF33', font=('Verdana', 20, 'bold'))
	printText.tag_configure('color', foreground='#476042',font=('Tempus Sans ITC', 14, 'bold'))
	printText.tag_configure('abkeyword', background='#FFFF33',foreground='#476042',font=('Tempus Sans ITC', 14, 'bold'))
	printText.tag_bind('follow', '<1>', lambda e, t=printText: t.insert(END, "Not now, maybe later!"))
	printText.insert(END, "\n", 'big')
	#顯示title
	for word in title.split(' '):
		if lemmakey == lemma(word):
			printText.insert(END, word+" ", 'tikeyword')
		else:
			printText.insert(END, word+" ", 'big')
	printText.insert(END, "\n\n", 'big')
	#顯示abstract
	for word in abstract.split(' '):
		if lemmakey == lemma(word):
			printText.insert(END, word+" ", 'abkeyword')
		else:
			printText.insert(END, word+" ", 'color')
	#顯示Author
	printText.insert(END, '\n\n'+author+'\n', 'follow')

else:
	alltext = fr.read()
	#留言
	textpat = re.compile(r'\n[\W]{4}"text": "(.+)",')
	textmatch = textpat.findall(alltext)
	#時間
	timepat = re.compile(r'\n[\W]{4}"created_at": "(.+)",')
	timematch = timepat.findall(alltext)
	#留言者
	userpat = re.compile(r'\n[\W]{8}"screen_name": "(.+)",')
	usermatch = userpat.findall(alltext)

	#顯示視窗
	printText.tag_configure('name', font=('Verdana', 14, 'bold'))
	printText.tag_configure('mesg', foreground='#476042',font=('Tempus Sans ITC', 14, 'bold'))
	printText.tag_configure('keyword', background='#FFFF33',foreground='#476042',font=('Tempus Sans ITC', 14, 'bold'))
	printText.tag_bind('time', '<1>', lambda e, t=printText: t.insert(END, "Not now, maybe later!"))

	#顯示文字
	text = ""
	for i in range(len(textmatch)):
		printText.insert(END, "\n" + usermatch[i] + " ", 'name')
		for word in textmatch[i]:
			if lemmakey == lemma(word):
				printText.insert(END, word, 'keyword')
			else:
				printText.insert(END, word, 'mesg')
		printText.insert(END, "\n")
		text += (textmatch[i] + " ")
		printText.insert(END, "\n" + timematch[i] + "\n", 'time')

#先輸出部分資訊
#顯示此檔案的字元數
printText.insert(END, '\n字元數(不含空白)為：'+str(CountCharNum(text))+'\n', 'follow')
#顯示此檔案的字詞數
printText.insert(END, '\n單字數為：'+str(len(text.split(" ")))+'\n', 'follow')
printText.pack(side=LEFT)
scroll.pack(side=RIGHT, fill=Y)

#機器學習mlp
"""
train_fr = open(trainFile,"r")
traindata = []
#來建判斷斷句model
for line in train_fr.readlines():
	traindata.append(Content2wv(line))
targetlist = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0]
print("開始train")
cls = svm.SVC()
print("fit")
cls.fit(traindata, targetlist)
print("輸出model")
#保存Model
with open('eosModel.pickle', 'wb') as f:
	pickle.dump(cls, f)
"""
#讀取Model
with open(trainFile, 'rb') as f:
	cls = pickle.load(f)

index = 1
endChar = ['.','!','?']
num = 0
en = 0
print("在做斷句分析！")
while en != 100:
	tmpIndex = find_NthLi(text,endChar,index)+1
	tmptext = text[:tmpIndex]
	testdata = Content2wv(tmptext)
	predictions = cls.predict([testdata])

	if predictions[0] == 1:
		text = text[tmpIndex:].strip()
		index = 0
		num += 1
		en = 0
	else:
		en+=1
		index = tmpIndex

printText.insert(END, '\n句數為：'+str(num)+'\n', 'follow')

window.mainloop()
