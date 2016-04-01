from collections import Counter
import random
import os

from nltk import word_tokenize

from nltk.corpus import stopwords
from nltk import FreqDist

import pickle
import itertools
from random import shuffle

import nltk
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

import sklearn
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.metrics import accuracy_score

from Scrapper import *

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
    try:
        os.remove('train.data')
        os.remove('test.data')
    except OSError:
        pass


# 2.1 Use all words as features
def bag_of_words(words):
    return dict([(word, True) for word in words])


# 2.2 Use bigrams as features (use chi square chose top 200 bigrams)
def bigrams(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return bag_of_words(bigrams)


def most_common_features(dataset, num_words):
    """
    Gets the :param num_words most frequent words
    from the given :param dataset.
    Does not include stop words
    :param dataset:
    :param num_words:
    :return: list of most common features
    """
    words_in_x = []
    for x in dataset:
        for word in word_tokenize(x):
            word = word.lower()
            for i in chars or i in positions:
                word = word.replace(i, '')
            if word.isdigit() or re.compile('www.*').match(word) is not None \
                    or word in stopwords.words('english') or len(word) <= 2:
                continue
            words_in_x.append(word)
    fd = FreqDist(words_in_x)
    return dict(fd.most_common(num_words)).keys()


def find_freq_of_features(data, features):
    """
    Finds the frequency of most common features in this
    data
    :param data:
    :param features:
    :return: dict
    """
    freq_features = dict.fromkeys(features, 0)
    for word in word_tokenize(data):
        if word in features:
            freq_features[word] += 1
    return freq_features


def map_features_to_dict(features):
    feature_dict = {}
    tmp_num = 1
    for k in features:
        feature_dict[k] = tmp_num
        tmp_num += 1
    return feature_dict


def set_up_train_and_test_files(train_dataset_size=100, test_dataset_size=100, num_features=50):
    """
    Adds data to train and test files,
    that conforms to the SVM_Light
    :param num_features: number of most frequent words to consider
    :param test_dataset_size:
    :param train_dataset_size:
    :return:
    """
    debates = read_debates_from_file('abortion_debates.txt')

    train_features = []
    train_targets = []
    test_features = []
    test_targets = []

    # shuffles the data randomly, so we don't get
    # the same data point every time
    debates = list(debates)
    random.shuffle(debates)

    train_debates = debates[0:train_dataset_size]
    test_debates = debates[train_dataset_size + 1:train_dataset_size + test_dataset_size]

    # SETS UP TRAINING DATA FILE
    print 'Setting up training data...'
    frequency_words = most_common_features([y.con_data for x in train_debates for y in x.rounds] +
                                           [y.pro_data for x in train_debates for y in x.rounds] +
                                           [y.con_data for x in test_debates for y in x.rounds] +
                                           [y.pro_data for x in test_debates for y in x.rounds],
                                           num_features)

    freq_mapped_indices = map_features_to_dict(frequency_words)

    for debate in train_debates:
        for round in debate.rounds:
            pro_features = [0] * len(freq_mapped_indices)
            con_features = [0] * len(freq_mapped_indices)

            # Prep pro data for SVM_Light
            train_targets.append(1)
            counter_pro = find_freq_of_features(round.pro_data, frequency_words)
            for k, v in counter_pro.items():
                pro_features[freq_mapped_indices[k] - 1] = counter_pro[k] / float(num_features)
            train_features.append(pro_features)

            # Prep con data for SVM_Light
            train_targets.append(-1)
            counter_con = find_freq_of_features(round.con_data, frequency_words)
            for k, v in counter_con.items():
                con_features[freq_mapped_indices[k] - 1] = counter_con[k] / float(num_features)
            train_features.append(con_features)

    for debate in test_debates:
        for round in debate.rounds:
            pro_features = [0] * len(freq_mapped_indices)
            con_features = [0] * len(freq_mapped_indices)

            # Prep pro data for SVM_Light
            test_targets.append(1)
            counter_pro = find_freq_of_features(round.pro_data, frequency_words)
            for k, v in counter_pro.items():
                pro_features[freq_mapped_indices[k] - 1] = counter_pro[k] / float(num_features)
            test_features.append(pro_features)

            # Prep con data for SVM_Light
            test_targets.append(-1)
            counter_con = find_freq_of_features(round.con_data, frequency_words)
            for k, v in counter_con.items():
                con_features[freq_mapped_indices[k] - 1] = counter_con[k] / float(num_features)
            test_features.append(con_features)
    return train_features, train_targets, test_features, test_targets


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
