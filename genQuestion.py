import pymongo
import collections

client = pymongo.MongoClient("localhost", 27017)
db = client.oborobot

def gen_question(target_str, hinsiType):
    if hinsiType == 'properNoun':
        return 'それは' + target_str + 'に関連がある?'
    elif hinsiType == 'noun':
        return 'それは' + target_str + 'に関係しそう?'
    elif hinsiType == 'adjective':
        return 'それは' + target_str + 'なイメージがある?'
    elif hinsiType == 'verb':
        return 'それは何かの' + target_str + 'に関係する?'

def remove_duplication(hinsi_list):
    upper_key_list = {}
    for v in list(set(hinsi_list)):
        upper_key_list[v.upper()] = v.lower()

    r = []
    for key in upper_key_list:
        r.append(upper_key_list[key])

    return r

proper_noun_list = []
for obj in db.word.find({"type": "ProperNoun"}):
    if obj['jp_nickname'] == '':
        proper_noun_list.append(gen_question(obj['value'], 'properNoun'))
    else:
         proper_noun_list.append(gen_question(obj['value'], 'properNoun'))
         if obj['value'] != obj['jp_nickname']:
            proper_noun_list.append(gen_question(obj['jp_nickname'], 'properNoun'))

print(remove_duplication(proper_noun_list))
print()
noun_list = []
for obj in db.word.find({"type": "Noun"}):
    if obj['jp_nickname'] == '':
        noun_list.append(gen_question(obj['value'], 'noun'))
    else:
         noun_list.append(gen_question(obj['value'], 'noun'))
         if obj['value'] != obj['jp_nickname']:
            noun_list.append(gen_question(obj['jp_nickname'], 'noun'))

print(remove_duplication(noun_list))
print()
adjective_list = []
for obj in db.word.find({"type": "Adjective"}):
    if obj['jp_nickname'] == '':
        adjective_list.append(gen_question(obj['value'], 'adjective'))
    else:
         adjective_list.append(gen_question(obj['value'], 'adjective'))
         if obj['value'] != obj['jp_nickname']:
            adjective_list.append(gen_question(obj['jp_nickname'], 'adjective'))

print(remove_duplication(adjective_list))
print()
verb_list = []
for obj in db.word.find({"type": "Verb"}):
    if obj['jp_nickname'] == '':
        verb_list.append(gen_question(obj['value'], 'verb'))
    else:
         verb_list.append(gen_question(obj['value'], 'verb'))
         if obj['value'] != obj['jp_nickname']:
            verb_list.append(gen_question(obj['jp_nickname'], 'verb'))

print(remove_duplication(verb_list))
print()