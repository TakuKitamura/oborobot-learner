# from gensim.models import KeyedVectors
# model_dir = './entity_vector.model.bin'
# model = KeyedVectors.load_word2vec_format(model_dir, binary=True)
# results = model.most_similar(u'Server')
# for result in results:
#     print(result)

# # results = model.most_similar(u'[手品]')
# # for result in results:
# #     print(result)

import io

def load_vectors(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = map(float, tokens[1:])
        print(tokens[0])
    return data

load_vectors('crawl-300d-2M.vec')