from collections import Counter
import re
import operator
import random
import argparse

from nltk import word_tokenize
from nltk.corpus import stopwords

from sklearn import svm

from Scrapper import read_debates_from_file
from Util import *

__author__ = 'drandhaw'


parser = argparse.ArgumentParser()
parser.add_argument('-tr', '--trainsetsize', required=True, default=100, type=int, help='Number of data points to use for training')
parser.add_argument('-tt', '--testsetsize', required=True, default=100, type=int, help='Number of data points to use for testing')
args = vars(parser.parse_args())

if __name__ == "__main__":
    train, test = set_up_train_and_test_files(args['trainsetsize'], args['testsetsize'])
    train_features, train_targets, test_features, test_targets = get_data_in_sklearn_svm_format(train, test)

    clf = svm.SVC()
    clf.fit(train_features, train_targets)

    
    print 'Predicting on test data ...'
    predict = clf.predict(test_features)
    total_correct = 0
    for i in range(len(predict)):
        if predict[i] == test_targets[i]:
            total_correct += 1
    print 'Accuracy=' + str(total_correct / float(len(predict)))

    cleanup_files()
