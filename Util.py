from collections import Counter
import re
import operator
import random
import argparse
import os

from nltk import word_tokenize
from nltk.corpus import stopwords

from sklearn import svm

from Scrapper import read_debates_from_file
from Util import *

__author__ = 'drandhaw'

chars = '~`!@#$%^&*()_-+={}|:"<>?,./;[]\\\''
positions = ['nd', 'rd', 'th']


def write_lines_to_file(filename, lines=[]):
    """
    writes lines to the file with filename
    :param filename:
    :param lines: a list of lines
    :return:
    """
    with open(filename, mode='w') as output_file:
        for line in lines:
            output_file.write(line)
            output_file.write('\n')


def cleanup_files():
    os.remove('train.data')
    os.remove('test.data')

def set_up_train_and_test_files(train_dataset_size=100, test_dataset_size=100):
    """
    Adds data to train and test files,
    that conforms to the SVM_Light
    :param test_dataset_size:
    :param train_dataset_size:
    :return:
    """
    debates = read_debates_from_file('abortion_debates.txt')
    stop_words = stopwords.words('english')

    con_data_dict = {}
    pro_data_dict = {}

    max_con_value = 1
    max_pro_value = 1

    train_lines = []
    test_lines = []

    frequency_words_train_data = {}

    # shuffles the data randomly, so we don't get
    # the same data point every time
    debates = list(debates)
    random.shuffle(debates)

    train_debates = debates[0:train_dataset_size]
    test_debates = debates[train_dataset_size + 1:train_dataset_size + test_dataset_size]

    # SETS UP TRAINING DATA FILE
    print 'Setting up training data...'
    for debate in train_debates:
        for round in debate.rounds:
            svm_pro_target = '1'
            svm_con_target = '-1'

            # Prep pro data for SVM_Light
            for word in word_tokenize(round.pro_data):
                if word == '': continue
                word = word.lower()
                for i in chars or i in positions:
                    word = word.replace(i, '')
                if word.isdigit() \
                        or re.compile('www.*').match(word) is not None:
                    continue
                if word not in pro_data_dict and word not in stop_words:
                    pro_data_dict[word] = max_pro_value
                    max_pro_value += 1

                # increases the frequency count of word
                if word in frequency_words_train_data.keys():
                    frequency_words_train_data[word] += 1
                else:
                    frequency_words_train_data[word] = 1
            counter = Counter(word_tokenize(round.pro_data))

            # Writing PRO data in format to train file
            for k, v in sorted(pro_data_dict.items(), key=operator.itemgetter(1)):
                if counter[k] != 0:
                    svm_pro_target += ' ' + str(pro_data_dict[k]) + ':' + str(counter[k] / float(len(round.pro_data)))

            # Prep con data for SVM_Light
            for word in word_tokenize(round.con_data):
                if word == '': continue
                word = word.lower()
                for i in chars or i in positions:
                    word = word.replace(i, '')
                if word.replace('.', '').isdigit() \
                        or re.compile('www.*').match(word) is not None:
                    continue
                if word not in con_data_dict and word not in stop_words:
                    con_data_dict[word] = max_con_value
                    max_con_value += 1

                # increases the frequency count of word
                if word in frequency_words_train_data.keys():
                    frequency_words_train_data[word] += 1
                else:
                    frequency_words_train_data[word] = 1
            counter = Counter(word_tokenize(round.con_data))

            # Writing CON data in format to train file
            for k, v in sorted(con_data_dict.items(), key=operator.itemgetter(1)):
                if counter[k] != 0:
                    svm_con_target += ' ' + str(con_data_dict[k]) + ':' + str(counter[k] / float(len(round.con_data)))

            # print svm_con_line
            # print svm_pro_line

            train_lines.append(svm_con_target)
            train_lines.append(svm_pro_target)

    for debate in test_debates:
        for round in debate.rounds:
            svm_pro_target = '1'
            svm_con_target = '-1'

            # Prep pro data for SVM_Light
            for word in word_tokenize(round.pro_data):
                if word == '': continue
                word = word.lower()
                for i in chars or i in positions:
                    word = word.replace(i, '')
                if word.isdigit() \
                        or re.compile('www.*').match(word) is not None:
                    continue
                if word not in pro_data_dict and word not in stop_words:
                    pro_data_dict[word] = max_pro_value
                    max_pro_value += 1
            counter = Counter(word_tokenize(round.pro_data))

            # Writing PRO data in format to test file
            for k, v in sorted(pro_data_dict.items(), key=operator.itemgetter(1)):
                if counter[k] != 0:
                    svm_pro_target += ' ' + str(pro_data_dict[k]) + ':' + str(counter[k] / float(len(round.pro_data)))

            # Prep con data for SVM_Light
            for word in word_tokenize(round.con_data):
                if word == '': continue
                word = word.lower()
                for i in chars or i in positions:
                    word = word.replace(i, '')
                if word.replace('.', '').isdigit() \
                        or re.compile('www.*').match(word) is not None:
                    continue
                if word not in con_data_dict and word not in stop_words:
                    con_data_dict[word] = max_con_value
                    max_con_value += 1
            counter = Counter(word_tokenize(round.con_data))

            # Writing CON1 data in format to test file
            for k, v in sorted(con_data_dict.items(), key=operator.itemgetter(1)):
                if counter[k] != 0:
                    svm_con_target += ' ' + str(con_data_dict[k]) + ':' + str(counter[k] / float(len(round.con_data)))

            test_lines.append(svm_con_target)
            test_lines.append(svm_pro_target)
    return train_lines, test_lines


def get_features_with_most_frequency(total_feature_set, num_features):
    """
    Selects the top num_features from the total_feature_set
    and returns it
    Format of input is the same as
    :param total_feature_set:
    :param num_features:
    :return:
    """


def get_data_in_sklearn_svm_format(train_data, test_data):
    """
    :param train_data:
    :param test_data:
    :return train_features, train_targets, test_features, test_targets
    """
    sklearn_train_features = []
    sklearn_train_targets = []
    sklearn_test_features = []
    sklearn_test_targets = []

    # Set up train data
    for single_feature_set in train_data:
        single_feature_set = single_feature_set.split(' ')
        sklearn_train_targets.append(single_feature_set[0])
        tmp_value_set = []
        for feature_value in single_feature_set[1:]:
            feature = int(feature_value.split(':')[0])
            value = float(feature_value.split(':')[1])
            while len(tmp_value_set) != feature + 1:
                tmp_value_set.append(0)
            tmp_value_set[feature] = value
        sklearn_train_features.append(tmp_value_set)

    # Set up test data
    for single_feature_set in test_data:
        single_feature_set = single_feature_set.split(' ')
        sklearn_test_targets.append(single_feature_set[0])
        tmp_value_set = []
        for feature_value in single_feature_set[1:]:
            feature = int(feature_value.split(':')[0])
            value = float(feature_value.split(':')[1])
            while len(tmp_value_set) != feature + 1:
                tmp_value_set.append(0)
            tmp_value_set[feature] = value
        sklearn_test_features.append(tmp_value_set)

    # Matching matrix size of all items
    max_length = max(len(max(sklearn_train_features, key=len)), len(max(sklearn_test_features, key=len)))
    for j in range(len(sklearn_train_features)):
        if len(sklearn_train_features[j]) < max_length:
            sklearn_train_features[j] = sklearn_train_features[j] + (max_length - len(sklearn_train_features[j])) * [0]

    for i in range(len(sklearn_test_features)):
        if len(sklearn_test_features[i]) < max_length:
            sklearn_test_features[i] = sklearn_test_features[i] + (max_length - len(sklearn_test_features[i])) * [0]

    return sklearn_train_features, sklearn_train_targets, sklearn_test_features, sklearn_test_targets
