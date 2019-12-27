# import MeCab
import numpy as np
from gensim.models import KeyedVectors, Word2Vec
import unicodedata
from janome.tokenizer import Tokenizer
import nltk

jp_tokennizer = Tokenizer('../oborobot-analyzer/neologd')

def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name \
        or "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False

def tokenize(text):
    if is_japanese(text):
        return jp_tokennizer.tokenize(text, wakati=True)
    else:
        return nltk.word_tokenize(text)
    # wakati = MeCab.Tagger("-O wakati")
    # wakati.parse("")
    # return wakati.parse(text).strip().split(" ")


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


class WED():
    """
    Word Embedding based Edit Distance
    https://arxiv.org/abs/1810.10752
    """

    def __init__(self, embedding, tokenizer, params):
        self.embedding = embedding
        self.tokenize = tokenize
        self.params = params

    def _word_similarity(self, w1, w2):
        if w1 == w2:
            score = 1
        elif w1 in self.embedding.vocab and w2 in self.embedding.vocab:
            score = sigmoid(self.params["w"] * self.embedding.similarity(w1, w2) + self.params["b"])
        else:
            score = 0
        return score

    def _largest_similarity(self, word, sentence, index):
        sim_list = [self._word_similarity(word, s) for i, s in enumerate(sentence) if i != index]
        if sim_list:
            return 1 - (self.params["l"] * np.max(sim_list) + self.params["m"])
        else:
            return 1

    def similar(self, s1, s2):
        s_a = self.tokenize(s1)
        s_b = self.tokenize(s2)
        print(s_a, s_b)

        l_a, l_b = len(s_a), len(s_b)
        dp = [[0] * (l_b + 1) for _ in range(l_a + 1)]

        for i in range(1, l_a + 1):
            dp[i][0] = dp[i - 1][0] + self._largest_similarity(s_a[i - 1], s_b, i - 1)

        for j in range(1, l_b + 1):
            dp[0][j] = dp[0][j - 1] + self._largest_similarity(s_b[j - 1], s_a, j - 1)

        for i in range(1, l_a + 1):
            for j in range(1, l_b + 1):
                insertion_cost = 1 - self._largest_similarity(s_b[j - 1], s_a,  i - 1)
                deletion_cost = 1 - self._largest_similarity(s_a[i - 1], s_b, j - 1)
                substitution_cost = 2 - 2 * self._word_similarity(s_a[i - 1], s_b[j - 1])
                dp[i][j] = min(dp[i][j - 1] + insertion_cost,
                               dp[i - 1][j] + deletion_cost,
                               dp[i - 1][j - 1] + substitution_cost)
        return dp[l_a][l_b]


if __name__ == "__main__":
    w2v_path = "vecData/wiki-news-300d-1M.vec.bin"
    model = KeyedVectors.load_word2vec_format(w2v_path, binary=True)
    params = {"w": 2, "b": 0, "l": 0.5, "m": 0.5}

    wed = WED(embedding=model, tokenizer=tokenize, params=params)
    # print(wed.similar("How large is the largest city in Alaska?", "The biggest city in Alaska is how big?"))
    print(wed.similar("今日は晴れです｡", "今日は晴れです｡"))
    # print(wed.similar("go api server", "api server go"))
    # print(wed.similar("api server", "api server go"))
    # print(wed.similar("api server", "api server go"))
    # print(wed.similar("私はクマです", "私はクマです"))
    # print(wed.similar("私は人間です", "私はクマです"))
    # print(wed.similar("今日の天気は晴れです｡", "あれ､やばすぎない"))
