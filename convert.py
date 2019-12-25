from gensim.models.keyedvectors import KeyedVectors

w2v_model = KeyedVectors.load_word2vec_format('wiki-news-300d-1M.vec', binary=False)
w2v_model.save_word2vec_format('wiki-news-300d-1M.vec.bin', binary=True)