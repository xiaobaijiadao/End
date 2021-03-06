from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import os
import pickle
from collections import Counter

# from pymongo import MongoClient, ASCENDING
# conn = MongoClient('172.19.241.248', 20000)
# db = conn['wangxiao']


def trans_data_to_file(path='data/data.csv', out_dir='data/trainSet/rank/tfidf/'):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    data = pd.read_csv(path)
    for cls, group in data.groupby('cls'):
        print(cls)
        id_list = group['id'].tolist()
        doc_list = group['token'].tolist()
        doc_list = list(map(lambda s: s.strip().replace('。', ' '), doc_list))
        res = {
            'id': id_list,
            'doc': doc_list,
        }
        with open(os.path.join(out_dir, str(cls) + '.pkl'), 'wb') as fp:
            pickle.dump(res, fp)


def read_data_from_dir(dir):
    # file_lists = os.listdir(dir)  # 列出文件夹下所有的目录与文件
    # for file in file_lists:
    #     cls, tp = file.split('_')
    #     if tp == 'id':
    #         print(cls)
    #         with open(os.path.join(dir, cls+'_id'), 'rb') as fp:
    #             docid_list = pickle.load(fp)
    #         with open(os.path.join(dir, cls+'_doc'), 'rb') as fp:
    #             corpus = pickle.load(fp)
    #         yield cls, docid_list, corpus

    names = ['9001', '9012', '9047', '9130', '9299', '9461', '9483', '9542', '9705', '9771',]
#     names = ['9483']

    for name in names:
        print(name)
        with open(os.path.join(dir, name + '.pkl'), 'rb') as fp:
            data = pickle.load(fp)
        print(len(data['id']), len(data['doc']))
        yield name, data['id'], data['doc']


class TfIdfVec():
    def __init__(self, corpus, docid_list, cls, min_count=None, num_limit=3000, word_dic_path=None):
        self.corpus = corpus
        self.docid_list = docid_list
        self.cls = cls
#         self.col = db['web_tfidf_' + cls]
#         self.col.create_index([('word', ASCENDING)])
        self.min_count = min_count
        self.num_limit = num_limit
        with open(word_dic_path, 'rb') as fp:
            word_dict = pickle.load(fp)
        self.word_dict = {word:index-1 for word,index in word_dict.items()}
        self.word_list = {index:word for word,index in self.word_dict.items()}

    def fit(self):
        print('train tfidf...')
        tfidfvector = TfidfVectorizer(vocabulary=self.word_dict)
#         print(self.corpus[0])
        matrix = tfidfvector.fit_transform(self.corpus)
        print(len(tfidfvector.get_feature_names()))
        return matrix

    def save_db(self, matrix):
#         print(matrix)
        nonzero = matrix.nonzero()
#         print(nonzero[0][0])
#         print(nonzero[1][0])
#         print(matrix.data[0])
        dic = {
            'doc': nonzero[0],
            'word': nonzero[1],
            'tfidf': matrix.data,
        }
        df = pd.DataFrame(dic)
#         print(len(df))
        buffer = []

        for word_index, group in df.groupby('word'):
            tmp = group.sort_values(by="tfidf", ascending=False)
            buffer.append({
                "word": self.word_list[word_index],
                "doc_tfidf": [{'doc': self.docid_list[doc_index], 'tfidf': tfidf} for doc_index, tfidf in
                              zip(tmp['doc'].tolist()[:self.num_limit], tmp['tfidf'].tolist()[:self.num_limit])]
            })

#             if len(buffer) > 1000:
#                 self.col.insert(buffer)
#                 buffer.clear()
#         if len(buffer) > 0:
#             self.col.insert(buffer)
#             buffer.clear()
        
    def save_key_words(self, matrix, out_path):
        nonzero = matrix.nonzero()
        dic = {
            'doc': nonzero[0],
            'word': nonzero[1],
            'tfidf': matrix.data,
        }
        df = pd.DataFrame(dic)
        print(len(df))
        res = []

        def gen_key_word(df, word_list, docid_list, limit=10):
            doc_index = df['doc'].tolist()[0]
            tmp = df.sort_values(by="tfidf", ascending=False)
            key_words = [word_list[word_index] for word_index in tmp['word'].tolist()[:limit]]
            key_words = ' '.join(filter(lambda x:x not in ['ldquo', 'rdquo'], key_words))
            res.append([docid_list[doc_index], key_words])

        df.groupby('doc').apply(gen_key_word, word_list=self.word_list, docid_list=self.docid_list)

        key_words_df = pd.DataFrame(res, columns=['docId', 'keywords'])
        key_words_df.to_csv(out_path, index=0)
        print('key words finish!')

    def run(self):
        matrix = self.fit()
        print(len(self.word_list))
        self.save_key_words(matrix, 'data/trainSet/keywords'+self.cls+'.csv')
#         self.save_db(matrix)
        print(self.cls, ' finished!')
#         self.save_dict(os.path.join('../data/trainSet/rank/dict/', self.cls+'_dictionary.dic'))
    
    def save_dict(self, path):
        word_dic = {word:index+1 for word, index in self.word_dict.items()}
        with open(path, 'wb') as fp:
            pickle.dump(word_dic, fp)


if __name__ == '__main__':
#     trans_data_to_file(path='../data/data.csv', out_dir='../data/trainSet/rank/tfidf/')

    for cls, docid_list, corpus in read_data_from_dir(dir='../data/trainSet/rank/tfidf/'):
#         tiv = TfIdfVec(corpus, docid_list, cls, min_count=30, word_dic_path=os.path.join('../data/trainSet/rank/dict/', cls+'_dictionary.dic'))
        tiv = TfIdfVec(corpus, docid_list, cls, min_count=30)
        tiv.run() 

    print('Finished!')

