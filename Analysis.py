from collections import Counter

from nltk import word_tokenize

from Scrapper import *

import operator

__author__ = 'drandhaw'

debates = read_debates_from_file('abortion_debates.txt')

con_data_dict = {}
pro_data_dict = {}

max_con_value = 1
max_pro_value = 1

for debate in list(debates):
    print debate
    for round in debate.rounds:
        svm_pro_line = '1'
        svm_con_line = '-1'

        for word in word_tokenize(round.pro_data):
            if word not in pro_data_dict:
                pro_data_dict[word] = max_pro_value
                max_pro_value += 1
        counter = Counter(word_tokenize(round.pro_data))

        for k, v in sorted(pro_data_dict.items(), key=operator.itemgetter(1)):
            svm_pro_line += ' ' + str(pro_data_dict[k]) + ':' + str(counter[k] / float(len(round.pro_data)))

        print svm_pro_line

        for word in word_tokenize(round.con_data):
            if word not in con_data_dict:
                con_data_dict[word] = max_con_value
                max_con_value += 1
        counter = Counter(word_tokenize(round.con_data))

        for k, v in sorted(con_data_dict.items(), key=operator.itemgetter(1)):
            svm_con_line += ' ' + str(con_data_dict[k]) + ':' + str(counter[k] / float(len(round.con_data)))

        print svm_con_line



        break
    break
