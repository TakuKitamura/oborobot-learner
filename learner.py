import pymongo
from urllib.parse import urlparse
import collections
import random

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
            'url': [],
            'url_count': [],
            'user_rating': []
        },
    'objective_id': []
}
objective_id = 1

for clean_url in url_count_dict:
    explanatory_obj = predictor_dict['explanatory']
    explanatory_obj['url'].append(clean_url)
    explanatory_obj['url_count'].append(url_count_dict[clean_url])

    predictor_dict['objective_id'].append(objective_id)
    objective_id += 1


print(predictor_dict)
