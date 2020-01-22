
import random
import math
from pprint import pprint
import time
import pymongo

def randNum():
	return random.uniform(0, 10)

client = pymongo.MongoClient("localhost", 27017)
db = client.oborobot

articles = {}

for obj in db.word.find({'$or': [{'section_name': "description"} , {"section_name": "title"}], "lang":"ja", '$or': [{"type": "ProperNoun"} , {"type": "Noun"}]}):
	# print(obj)
	articles[obj['href']] = {
		'pos': [randNum(), randNum()],
		'words': [],
		'reward': 0.0,
		'f': 0.0,
		'url': obj['href']
	}




for obj in db.word.find({'$or': [{'section_name': "description"} , {"section_name": "title"}], "lang":"ja", '$or': [{"type": "ProperNoun"}, {"type": "Noun"}, {"type": "Adjective"}]}):
	articles[obj['href']]['words'].append(obj['value'].lower())
	articles[obj['href']]['words'] = list(set(articles[obj['href']]['words']))
	articles[obj['href']]['reward'] = len(articles[obj['href']]['words'])

# print(articles)
# exit(0)




# articles = {
# 	'記事1': {
# 		'pos': [randNum(), randNum()],
# 		'words': ['python', 'file'],
# 		'reward': 3,
# 		'f': 0.0,
# 		'url': 'a.com'

# 	},
# 	'記事2': {
# 		'pos': [randNum(), randNum()],
# 		'words': ['圧縮', 'エンコード'],
# 		'reward': 1,
# 		'f': 0.0,
# 		'url': 'b.com'
# 	},
# 	'記事3': {
# 		'pos': [randNum(), randNum()],
# 		'words': ['API', 'go'],
# 		'reward': 7,
# 		'f': 0.0,
# 		'url': 'c.com'
# 	},
# 	'記事4': {
# 		'pos': [randNum(), randNum()],
# 		'words': ['言語', '通信'],
# 		'reward': 9,
# 		'f': 0.0,
# 		'url': 'd.com'
# 	}
# }

request = {
	'pos': [0.0, 0.0],
	'reward': 1,
}

# わからないを追加
# position を3店､ もしくは2点



G = 6.67408 # * (10**-11)

def get_distance(x, y):
    d = math.sqrt((y[0] - x[0]) ** 2 + (y[1] - x[1]) ** 2)
    return d

while True:
	maxF = 0
	fMaxArticleName = ''
	request['pos'][0] = randNum()
	request['pos'][1] = randNum()

	print('スタート')
	blackLists = []
	selectArticles = []
	while True:
		for articleName in articles:
			article = articles[articleName]
			# print(article)
			# print(random.uniform(0, 100))

			# x1, y1, x2, y2 = 1.0, 2.0, 2.0, 3.0
			r = get_distance(request['pos'], article['pos'])
			m1 = article['reward']
			m2 = request['reward']
			# f = G * ((m1 * m2)/(r**2))
			f = m1 / r
			if f > maxF:
				maxF = f
				fMaxArticleName = articleName
			# print(article, request)
			# print(f)
			article['f'] = f

		maxArticle = articles[fMaxArticleName]
		blackLists.append(fMaxArticleName)
		# articles.pop(fMaxArticleName)

		# pprint(articles)

		selectWordsQuestion = ''
		wordCount = 0
		# selectWordMap = {}
		tempSelectWordMap = {}
		for articleName in articles:
			if articleName not in blackLists:
				# print("black:",blackLists)
				article = articles[articleName]
				for i in range(0, len(article['words'])):
					word = article['words'][i]
					# selectWordsQuestion += str(wordCount+1) + ':' + word + ', '
					if word not in tempSelectWordMap.keys():
						tempSelectWordMap[word] = [articleName]
					else:
						tempSelectWordMap[word].append(articleName)
					# selectWordMap[wordCount+1] = articleName
					wordCount += 1

		selectWordMap = []
		i = 0
		for articleName in tempSelectWordMap:
			selectWordMap.append({'id': i, 'articleName': articleName, 'urlList': tempSelectWordMap[articleName]})
			i+=1
		# pprint(selectWordMap)

		for wordDict in selectWordMap:
			selectWordsQuestion += str(wordDict['id']+1) + ':' + wordDict['articleName'] + ', '
		# exit(0)
		# pprint(articles)
		answer = input(fMaxArticleName + ' 役に立つ? ')
		if answer == 'y':
			# 役に立つと言われた｡
			articles[fMaxArticleName]['reward'] += 5
			# pprint(articles)
			break

		# 役に立たないと言われた
		articles[fMaxArticleName]['reward'] -= 10
		if articles[fMaxArticleName]['reward'] < 0:
			articles[fMaxArticleName]['reward'] = 0.1

		# pprint(articles)

		maxF = 0
		start = time.time()
		print('前の単語にはどの単語が関係ありそう?', selectWordsQuestion)
		selectWordNum = int(input())
		if selectWordNum >= 1 and selectWordNum <= len(selectWordMap) :
			# selectArticleName = selectWordMap[selectWordNum-1]['articleName']
			# selectArticles.append(selectArticleName)
			# articles[selectArticleName]['reward'] += 5
			# print("select", selectArticles)

			selectArticleURList = selectWordMap[selectWordNum-1]['urlList']
			# print(selectArticleURList)
			groupArticles = []
			sumMX = 0.0
			sumMY = 0.0
			sumReward = 0.0 # m
			for url in selectArticleURList:
				articles[url]['reward'] += 5
				sumReward += articles[url]['reward']
				sumMX += articles[url]['reward'] * articles[url]['pos'][0] # m * xn
				sumMY += articles[url]['reward'] * articles[url]['pos'][1]
				groupArticles.append(articles[url])

			# 複数点の重心
			xg = sumMX / sumReward
			yg = sumMY / sumReward

			for url in selectArticleURList:
				# ここでは､重心と現在の座標の中点
				articles[url]['pos'][0] = (articles[url]['pos'][0] + xg) / 2
				articles[url]['pos'][1] = (articles[url]['pos'][1] + yg) / 2

			selectArticles.append(groupArticles)
			if len(selectArticles) > 1:
				compareArticles = selectArticles[len(selectArticles) - 2]
				print(compareArticles)
				print(selectArticles[len(selectArticles) - 1])

				sumMXCompare = 0.0
				sumMYCompare = 0.0
				sumRewardCompare = 0.0 # m

				for compareArticle in compareArticles:
					sumRewardCompare += compareArticle['reward']
					sumMXCompare += compareArticle['reward'] * compareArticle['pos'][0] # m * xn
					sumMYCompare += compareArticle['reward'] * compareArticle['pos'][1]

				# 複数点の重心
				xgCompare = sumMXCompare / sumRewardCompare
				ygCompare = sumMYCompare / sumRewardCompare

				# 2物体の重心 (m1x1 + m2x2) / m1 + m2
				twoCenterXg = ((sumReward * xg) + (sumRewardCompare * xgCompare)) / (sumReward + sumRewardCompare)
				twoCenterYg = ((sumReward * yg) + (sumRewardCompare * ygCompare)) / (sumReward + sumRewardCompare)

				print(twoCenterXg, twoCenterYg)

				print(111, selectArticles)
				for groupArticles in selectArticles:
					for articleDict in groupArticles:
						# print(articleDict)
					# ここでは､重心と現在の座標の中点
						articleDict['pos'][0] = (articleDict['pos'][0] + twoCenterXg) / 2
						articleDict['pos'][1] = (articleDict['pos'][1] + twoCenterYg) / 2

				print(222, selectArticles)

				# articleAPos = articles[selectArticles[len(selectArticles) - 2]]['pos']
				# articleBPos = articles[selectArticles[len(selectArticles) - 1]]['pos']
				# articleCenterX = (articleAPos[0] + articleBPos[0]) / 2
				# articleCenterY = (articleAPos[1] + articleBPos[1]) / 2
				# # articleCenterPos = [articleCenterX, articleCenterY]
				# articleAPos[0] = (articleAPos[0] + articleCenterX) / 2
				# articleAPos[1] = (articleAPos[1] + articleCenterY) / 2

				# articleBPos[0] = (articleBPos[0] + articleCenterX) / 2
				# articleBPos[1] = (articleBPos[1] + articleCenterY) / 2
			# pprint(articles)

		else:
			pass
			# 選択肢の候補単語リストの中に､良い記事出典がなかった
			# for obj in selectWordMap:
			# 	# print(selectWordNum)
			# 	articles[obj[selectWordNum]-1]]['reward'] -= 10
			# 	if articles[obj[selectWordNum]-1]]['reward'] < 0:
			# 		articles[obj[selectWordNum]-1]]['reward'] = 0.1
			# pprint(articles)
			# evaluate(articles, original_articles, rewards)
		# print(time.time() - start, "sec")