import pymongo
from urllib.parse import urlparse
import collections
import random

from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression

from decimal import Decimal, ROUND_HALF_UP

def rounding(v):
    return int(Decimal(str(v)).quantize(Decimal('1'), ROUND_HALF_UP))

def get_clean_url(url):
    parsed_url = urlparse(url)
    clean_url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
    return clean_url
client = pymongo.MongoClient("localhost", 27017)
db = client.oborobot

url_list = []
for obj in db.favorite.find({'is_checked': True}):
    url = obj['href']
    clean_url = get_clean_url(url)
    url_list.append(clean_url)

# print(url_list)
# print(collections.Counter(url_list))
random.shuffle(url_list)
url_count_dict = collections.Counter(url_list)

predictor_dict = {
    'explanatory':
        {
            'url_count': [],
            'user_rating': []
        },
    'objective_id': [],
    'url': [],
}
objective_id = 1

for clean_url in url_count_dict:
    explanatory_dict = predictor_dict['explanatory']
    explanatory_dict['url_count'].append(url_count_dict[clean_url])
    explanatory_dict['user_rating'].append(url_count_dict[clean_url] * 10)

    predictor_dict['objective_id'].append(objective_id)
    predictor_dict['url'].append(clean_url)
    objective_id += 1

print('predictor_dict:', predictor_dict)

X = []
y = []

for i in range(0, objective_id - 1):
    explanatory_dict = predictor_dict['explanatory']
    X.append([explanatory_dict['url_count'][i], explanatory_dict['user_rating'][i]])
    y.append(predictor_dict['objective_id'][i])

regr = RandomForestRegressor(max_depth=2, random_state=0)
regr.fit(X, y)
print('X:', X ,'| Y:', y)
print('feature_importances_:', regr.feature_importances_)
predict_value = [[60, 600]]
predicted_value = regr.predict(predict_value)[0]
print('predicted_value:', predicted_value)
predicted_object_id = rounding(predicted_value)
print('predicted_object_id:', predicted_object_id)
print('predicted_url:', predictor_dict['url'][predicted_object_id - 1])
