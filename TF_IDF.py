import jieba
import os
from math import log
from operator import itemgetter


class tf_idf:
    def __init__(self):
        self.files = {}
        self.corpus = {}
        self.stop_words = set(())
        content = open('cn_stopwords.txt', 'rb').read().decode('utf-8')
        for line in content.splitlines():
            self.stop_words.add(line)

    def add_file(self, file_name):
        # Load data and cut
        content = open(file_name, 'rb').read() if file_name[0] == '/' or file_name[0] == 'C' else open('C:\Users\Administrator\570-Program' + file_name, 'rb').read()
        words = jieba.cut(content)

        # Build dictionary
        dictionary = {}
        for w in words:
            if len(w.strip()) < 2 or w.lower() in self.stop_words:
                continue
            dictionary[w] = dictionary.get(w, 0.0) + 1.0
            self.corpus[w] = self.corpus.get(w, 0.0) + 1.0

        # Get term frequency
        total = sum(dictionary.values())
        for k in dictionary:
            dictionary[k] /= total

        # Add tf to the corpus
        self.files[file_name] = dictionary

    def get_tf_idf(self, file_name, top_k):
        # Get inverse document frequency
        tf_idf_of_file = {}
        for w in self.corpus.keys():
            w_in_f = 1.0
            for f in self.files:
                if w in self.files[f]:
                    w_in_f += 1.0
            # Get tf-idf
            if w in self.files[file_name]:
                tf_idf_of_file[w] = log(len(self.files) / w_in_f) * self.files[file_name][w]
        # Top-K result of tf-idf
        tags = sorted(tf_idf_of_file.items(), key=itemgetter(1), reverse=True)
        return tags[:top_k]



if __name__ == "__main__":
    table = tf_idf()
    folder_name = 'up'
    dir = os.path.dirname(__file__)
    folder = os.path.join(dir, 'C:\Users\Administrator\570-Program' + folder_name)
    num_of_files = len([name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name))]) + 1

    for x in range(1, num_of_files):
        file_name = folder_name + '/' + str(x).zfill(2) + '.txt'
        table.add_file(file_name)

    top_k = 30
    for x in range(1, num_of_files):
        target_file = folder_name + '/' + str(x).zfill(2) + '.txt'
        print('Top ' + str(top_k) + ' of tf-idf in ' + target_file + ' : ')
        print(table.get_tf_idf(target_file, top_k))
        print()

