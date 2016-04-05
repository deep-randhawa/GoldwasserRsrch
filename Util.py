import random
import os

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk import BigramCollocationFinder, BigramAssocMeasures

import itertools

from Scrapper import *

__author__ = 'drandhaw'

chars = '~`!@#$%^&*()_-+={}|:"<>?,./;[]\\\''
positions = ['nd', 'rd', 'th']
stop_words = stopwords.words('english')


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


def is_feature_relevant(feature):
    """
    Checks is the feature should be considered or not
    :param feature:
    :return:
    """
    if type(feature) is not str and type(feature) is not unicode:
        return False
    feature = feature.lower()
    for i in chars:
        feature = feature.replace(i, '')
    for i in positions:
        feature = feature.replace(i, '')
    if feature.isdigit() or re.compile('www.*').match(feature) is not None \
            or feature in stop_words or len(feature) <= 2:
        return False
    return True


def most_common_bigrams(all_words, num_bigrams):
    bigram_finder = BigramCollocationFinder.from_words(all_words)
    bigram_freq = dict(bigram_finder.ngram_fd.viewitems())
    for k, v in bigram_freq.items():
        if not is_feature_relevant(k[0]) or not is_feature_relevant(k[1]):
            del bigram_freq[k]

    fd =  FreqDist(bigram_freq)
    return dict(fd.most_common(num_bigrams)).keys()


def most_common_single_features(all_words, num_words):
    """
    Gets the :param num_words most frequent words
    from the given :param dataset.
    Does not include stop words
    :param dataset:
    :param num_words:
    :return: list of most common features
    """
    words_in_x = []
    for word in all_words:
        if is_feature_relevant(word):
            words_in_x.append(word)
    fd = FreqDist(words_in_x)
    return dict(fd.most_common(num_words)).keys()


def find_freq_of_features(local_features, imp_feature_set):
    """
    Finds the frequency of most common features in this
    data
    :param data:
    :param features:
    :return: dict
    """
    local_bigram_features = dict(BigramCollocationFinder.from_words(local_features).ngram_fd.viewitems())
    local_freq_features = dict.fromkeys(imp_feature_set, 0)
    for word in local_features:
        if word in imp_feature_set:
            local_freq_features[word] += 1

    for bigram in local_bigram_features:
        if bigram in imp_feature_set:
            local_freq_features[bigram] = local_bigram_features[bigram]

    return local_freq_features


def map_features_to_dict(features):
    feature_dict = {}
    tmp_num = 1
    for k in features:
        feature_dict[k] = tmp_num
        tmp_num += 1
    return feature_dict


def shuffle_data(features, targets, size_train=0.75, size_test=0.25):
    """
    Shuffles a set of features and targets,
    :returns train_features, train_targets, test_features, test_targets
    """
    combined = zip(features, targets)
    random.shuffle(combined)
    shuffled_features, shuffled_targets = zip(*combined)
    train_features = shuffled_features[:int(len(shuffled_features) * size_train)]
    train_targets = shuffled_targets[:int(len(shuffled_features) * size_train)]
    test_features = shuffled_features[int(len(shuffled_features) * size_test * -1):]
    test_targets = shuffled_targets[int(len(shuffled_features) * size_test * -1):]
    return train_features, train_targets, test_features, test_targets


def get_features_and_targets(num_features=50, size=200):
    """
    Adds data to train and test files,
    that conforms to the SVM_Light
    :param size: total #debates to consider, including training and test
    :param num_features: number of most frequent words to consider
    :return:
    """
    debates = list(read_debates_from_file('abortion_debates.txt'))
    features = []
    targets = []

    # shuffles the data randomly, so we don't get
    # the same data point every time
    random.shuffle(debates)
    debates = debates[0:size]

    # SETS UP TRAINING DATA FILE
    print 'Setting up training data...'
    all_words = [y.con_data for x in debates for y in x.rounds] + \
                [y.pro_data for x in debates for y in x.rounds]
    all_words = list(itertools.chain(*([word_tokenize(x) for x in all_words])))

    frequent_single_features = most_common_single_features(all_words, num_features)
    frequent_bigrams = most_common_bigrams(all_words, num_features * 10)

    all_features = frequent_single_features + frequent_bigrams

    freq_mapped_indices = map_features_to_dict(all_features)

    for debate in debates:
        for round in debate.rounds:
            pro_features = [0] * len(freq_mapped_indices)
            con_features = [0] * len(freq_mapped_indices)

            # Prep pro data
            targets.append(1)
            counter_pro = find_freq_of_features(word_tokenize(round.pro_data), all_features)
            for k, v in counter_pro.items():
                pro_features[freq_mapped_indices[k] - 1] = counter_pro[k] / float(num_features)
            features.append(pro_features)

            # Prep con data
            targets.append(-1)
            counter_con = find_freq_of_features(word_tokenize(round.con_data), all_features)
            for k, v in counter_con.items():
                con_features[freq_mapped_indices[k] - 1] = counter_con[k] / float(num_features)
            features.append(con_features)
    return features, targets


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
