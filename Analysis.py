from Util import *
from sklearn import tree
import argparse
from sklearn import svm
import itertools
import operator
import numpy as np

__author__ = 'drandhaw'

parser = argparse.ArgumentParser()
parser.add_argument('-tr', '--trainsetsize', required=False, default=100, type=int,
                    help='# of data points for training')
parser.add_argument('-tt', '--testsetsize', required=False, default=100, type=int, help='# of data points for testing')
parser.add_argument('-nf', '--numfeatures', required=False, default=100, type=int,
                    help='# of most frequent features to consider')
args = vars(parser.parse_args())


def analyse_data():
    features, targets = get_features_and_targets(args['numfeatures'], 200)

    print '5 fold testing...'
    svm_accuracy = []
    decisiontree_accuracy = []
    for i in range(1, 6):

        print 'Test run #' + str(i)
        train_features, train_targets, test_features, test_targets = shuffle_data(features, targets)

        clfsvm = svm.SVC()
        clfsvm.fit(train_features, train_targets)
        predictions = clfsvm.predict(test_features)
        total_correct = 0
        for j in range(len(predictions)):
            if predictions[j] == test_targets[j]:
                total_correct += 1
        svm_accuracy.append(total_correct / float(len(predictions)))
        # print 'SVM score:', clfsvm.score(test_features, test_targets)

        clfdecisiontree = tree.DecisionTreeClassifier()
        clfdecisiontree = clfdecisiontree.fit(train_features, train_targets)
        total_correct = 0
        predictions = clfdecisiontree.predict(test_features)
        for j in range(len(predictions)):
            if predictions[j] == test_targets[j]:
                total_correct += 1
        decisiontree_accuracy.append(total_correct / float(len(predictions)))
    print svm_accuracy
    print decisiontree_accuracy
    print '\tAccuracy w/ SVM=' + str(np.mean(svm_accuracy))
    print '\tAccuracy w/ Decision Tree=' + str(np.mean(decisiontree_accuracy))
    cleanup_files()


if __name__ == "__main__":
    # analyse_data()
    # debates = list(read_debates_from_file('abortion_debates.txt'))[:200]
    # dataset = [y.con_data for x in debates for y in x.rounds] + [y.pro_data for x in debates for y in x.rounds]
    # all_words = list(itertools.chain(*([word_tokenize(x) for x in dataset])))
    #
    # bigram_finder = BigramCollocationFinder.from_words(all_words)
    # bigrams = bigram_finder.nbest(BigramAssocMeasures.raw_freq, 500)
    #
    # bigram_freq = dict(bigram_finder.ngram_fd.viewitems())
    # for k, v in bigram_freq.items():
    #     if not is_feature_relevant(k[0]) or not is_feature_relevant(k[1]):
    #         del bigram_freq[k]
    #
    # bigram_freq = sorted(bigram_freq.items(), key=operator.itemgetter(1), reverse=True)
    pass
