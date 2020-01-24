
import random
import math
from pprint import pprint
import time
import pymongo
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib
from bottle import run, template, post, request, response, hook, route
import urllib.parse
import time

def randNum():
	return random.uniform(0, 1000)

def get_distance(x, y):
    d = math.sqrt((y[0] - x[0]) ** 2 + (y[1] - x[1]) ** 2)
    return d

def en(url):
	return urllib.parse.quote(url).replace(".", "%2E")

def de(url):
	return urllib.parse.unquote(url)

def main_loop(db, articles, request):
	# 以下ループ
	maxF = 0

	for articleName in articles:
		article = articles[articleName]
		r = get_distance(request['pos'], article['pos'])
		if r == 0:
			r += 1
		m1 = article['reward']
		# m2 = request['reward']
		# f = G * ((m1 * m2)/(r**2))
		f = m1 / (r**2)
		if f > maxF:
			maxF = f
		article['f'] = f
	sortedArticleNamesByReward =  sorted(articles, key=lambda x: (articles[x]['f']), reverse=True)
	# pprint(sortedArticleNamesByReward)

	recommendations = []
	wordCount = 0
	tempSelectWordMap = {}
	for encoded_url in sortedArticleNamesByReward:
		article = articles[encoded_url]
		# print(article)
		for i in range(0, len(article['words'])):
			word = article['words'][i]
			if word not in tempSelectWordMap.keys():
				tempSelectWordMap[word] = [articleName]
			else:
				tempSelectWordMap[word].append(articleName)
			wordCount += 1

		url = de(encoded_url)
		# print(url, 555)
		for obj in db.favorite.find({"href": url}):
			recommendations.append({'title': obj['title'], 'description': obj['description'], 'url': url})

	# pprint(recommendations)
	# exit(0)



	# for articleName in articles:
	# 	# plt.plot(article['pos'][0]d, article['pos'][1], marker='o', markersize=30)
	# 	# plt.annotate(article['wors'], xy=(article['pos'][0], article['pos'][1]))
	# 	article = articles[articleName]
	# 	for i in range(0, len(article['words'])):
	# 		word = article['words'][i]
	# 		if word not in tempSelectWordMap.keys():
	# 			tempSelectWordMap[word] = [articleName]
	# 		else:
	# 			tempSelectWordMap[word].append(articleName)
	# 		wordCount += 1
	# plt.pause(.01)
	selectWordMap = []
	i = 0
	for name in tempSelectWordMap:
		selectWordMap.append({'id': i, 'name': name, 'urlList': tempSelectWordMap[name]})
		i+=1

	r = {'articles': articles, 'choice': selectWordMap, 'recommendation': recommendations, 'request': request}
	return r


# user_id, lang, searchWords
def initCondidateList(userID, lang, searchValue):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.oborobot


	init = False

	articlesCollection = db.articles.find_one({})
	if articlesCollection == None:
		init = True

	articles = {}
	index = 0
	request = {}
	if init:
		for obj in db.word.find({'$or': [{'section_name': "description"} , {"section_name": "title"}], "lang":"ja", '$or': [{"type": "ProperNoun"} , {"type": "Noun"}]}):
			# print(obj)
			articles[en(obj['href'])] = {
				'pos': [randNum(), randNum()],
				'words': [],
				'reward': 1,
				'f': 0.0,
				'url': obj['href']
			}
			index += 1

		for obj in db.word.find({'$or': [{'section_name': "description"} , {"section_name": "title"}], "lang":"ja", '$or': [{"type": "ProperNoun"}, {"type": "Noun"}, {"type": "Adjective"}]}):
			articles[en(obj['href'])]['words'].append(obj['value'].lower())
			articles[en(obj['href'])]['words'] = list(set(articles[en(obj['href'])]['words']))
			articles[en(obj['href'])]['reward'] = len(articles[en(obj['href'])]['words'])

		request = {
			'pos': [0.0, 0.0],
			'reward': 1,
		}
	else:
		articlesCollection = db.articles.find_one({})
		articles = articlesCollection['articles']
		request = articlesCollection['request']

	searchWords = searchValue.split()
	selectArticleURList = []
	for articleName in articles:
		article = articles[articleName]
		words = article['words']
		for searchWord in searchWords:
			if searchWord in words:
				selectArticleURList.append(articleName)

	sumMX = 0.0
	sumMY = 0.0
	sumReward = 0.0 # m
	for url in selectArticleURList:
		# print(url)
		sumReward += articles[url]['reward']
		sumMX += articles[url]['reward'] * articles[url]['pos'][0] # m * xn
		sumMY += articles[url]['reward'] * articles[url]['pos'][1]

	# 複数点の重心
	if sumReward != 0:
		xg = sumMX / sumReward
		yg = sumMY / sumReward
	else:
		xg = 0
		yg = 0

	request['pos'][0] = xg
	request['pos'][1] = yg

	r = main_loop(db, articles, request)

	if init:
		db.articles.insert_one(
			{'user_id': userID, 'lang': lang, 'articles': r['articles'], 'choice': r['choice'], 'recommendation': r['recommendation'], 'request': request, 'selectArticles': {userID: {'groupArticles': [], 'choice_name': ''}}}
		)
	else:
		deleteColection = db.get_collection('articles')
		result = deleteColection.delete_many({})
		selectArticles = articlesCollection['selectArticles']
		selectArticles[userID] = {}
		selectArticles[userID]['groupArticles'] = []
		selectArticles[userID]['choice_name'] = ''
		db.articles.insert_one(
			{'user_id': userID, 'lang': lang, 'articles': r['articles'], 'choice': r['choice'], 'recommendation': r['recommendation'], 'request': request, 'selectArticles': selectArticles}
		)
	# print(result)

	choice = []
	for choiceDict in r['choice']:
		# print(choiceDict)
		choiceDict.pop('urlList')
		choice.append(choiceDict)

	return {'choice': choice, 'recommendation': r['recommendation']}

# user_id, lang, choice_id
def selectChoice(userID, choiceID, lang):
	client = pymongo.MongoClient("localhost", 27017)
	db = client.oborobot
	articlesCollection = db.articles.find_one()
	if articlesCollection == None:
		response.status = 500
		return {"message": 'user_id not found'}

	articles = articlesCollection['articles']
	# pprint(articles)
	selectWordMap = articlesCollection['choice']
	request = articlesCollection['request']
	# print(choiceID, 777)
	if choiceID < 0 or choiceID >= len(selectWordMap):
		response.status = 500
		return {"message": 'choiceID is invalid.'}

	selectArticleURList = selectWordMap[choiceID]['urlList']
	# print(selectArticleURList)

	selectArticles = articlesCollection['selectArticles']
	groupArticles = []
	sumMX = 0.0
	sumMY = 0.0
	sumReward = 0.0 # m
	for url in selectArticleURList:
		# articles[url]['reward'] += 5
		sumReward += articles[url]['reward']
		sumMX += articles[url]['reward'] * articles[url]['pos'][0] # m * xn
		sumMY += articles[url]['reward'] * articles[url]['pos'][1]
		groupArticles.append(articles[url])

	# 複数点の重心
	xg = sumMX / sumReward
	yg = sumMY / sumReward

	request['pos'][0] = (request['pos'][0] + xg) / 2
	request['pos'][1] = (request['pos'][1] + yg) / 2

	for url in selectArticleURList:
		# ここでは､重心と現在の座標の中点
		articles[url]['pos'][0] = (articles[url]['pos'][0] + xg) / 2
		articles[url]['pos'][1] = (articles[url]['pos'][1] + yg) / 2

	if userID not in selectArticles:
		response.status = 500
		return {"message": 'userID is invalid.'}
	selectArticles[userID]['groupArticles'].append(groupArticles)
	selectArticles[userID]['choice_name'] = selectWordMap[choiceID]['name']
	if len(selectArticles[userID]) > 1:
		compareArticles = selectArticles[userID]['groupArticles'][len(selectArticles[userID]['groupArticles']) - 2]
		# print(compareArticles)
		# print(selectArticles[len(selectArticles) - 1])

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

		# print(twoCenterXg, twoCenterYg)

		# print(111, selectArticles)
		for groupArticles in selectArticles[userID]['groupArticles']:
			for articleDict in groupArticles:
				# print(articleDict)
			# ここでは､重心と現在の座標の中点
				articleDict['pos'][0] = (articleDict['pos'][0] + twoCenterXg) / 2
				articleDict['pos'][1] = (articleDict['pos'][1] + twoCenterYg) / 2

	r = main_loop(db, articles, request)
	deleteColection = db.get_collection('articles')
	result = deleteColection.delete_many({})
	result=db.articles.insert_one(
		{'user_id': userID, 'lang': lang, 'articles': r['articles'], 'choice': r['choice'], 'recommendation': r['recommendation'], 'request': request, 'selectArticles': selectArticles}
	)

	plt.cla()
	plt.figure(figsize=(10, 5))
	plt.plot(request['pos'][0], request['pos'][1], marker='v', markersize=30)
	plt.annotate('現在地', xy=(request['pos'][0], request['pos'][1]))

	for articleURL in r['articles']:
		article = r['articles'][articleURL]
		plt.plot(article['pos'][0], article['pos'][1], marker='o', markersize=30)
		plt.annotate(article['words'], xy=(article['pos'][0], article['pos'][1]))


	plt.savefig('img/' + str(time.time()) + '_figure.png')
	# plt.pause(.01)
	# plt.close()

	choice = []
	for choiceDict in r['choice']:
		# print(choiceDict)
		choiceDict.pop('urlList')
		choice.append(choiceDict)

	return {'choice': choice, 'recommendation': r['recommendation']}

@hook('after_request')
def enable_cors():

    if not 'Origin' in request.headers.keys():
        return

    response.headers['Access-Control-Allow-Origin']  = request.headers['Origin']
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'

@route('<any:path>', method='OPTIONS')
def response_for_options(**kwargs):
    return {}

@post('/start')
def do_start():
	requestBody = request.json
	# user_id, lang, searchWords
	userID = requestBody['userID']
	lang = requestBody['lang']
	searchValue = requestBody['searchValue']
	r = initCondidateList(userID, lang, searchValue)
	print(userID, lang, searchValue)
	return r

# user_id, lang, choice_id
@post('/select')
def do_select():
	requestBody = request.json
	userID = requestBody['userID']
	lang = requestBody['lang']
	choiceID = requestBody['choiceID']
	r = selectChoice(userID, choiceID, lang)
	return r

run(host='localhost', port=8080, reloader=True)