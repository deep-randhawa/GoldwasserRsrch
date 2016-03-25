from Util import *
from sklearn import tree

__author__ = 'drandhaw'

parser = argparse.ArgumentParser()
parser.add_argument('-tr', '--trainsetsize', required=False, default=100, type=int, help='# of data points for training')
parser.add_argument('-tt', '--testsetsize', required=False, default=100, type=int, help='# of data points for testing')
parser.add_argument('-nf', '--numfeatures', required=False, default=100, type=int,
                    help='# of most frequent features to consider')
args = vars(parser.parse_args())

if __name__ == "__main__":
    train_features, train_targets, test_features, test_targets = set_up_train_and_test_files(args['trainsetsize'],
                                                                                             args['testsetsize'],
                                                                                             args['numfeatures'])

    print 'Predicting on test data ...'

    clfsvm = svm.SVC()
    clfsvm.fit(train_features, train_targets)

    predictions = clfsvm.predict(test_features)
    total_correct = 0
    for i in range(len(predictions)):
        if predictions[i] == test_targets[i]:
            total_correct += 1
    print 'Accuracy w/ SVM=' + str(total_correct / float(len(predictions)))

    clfdecisiontree = tree.DecisionTreeClassifier()
    clfdecisiontree = clfdecisiontree.fit(train_features, train_targets)

    total_correct = 0
    predictions = clfdecisiontree.predict(test_features)
    for i in range(len(predictions)):
        if predictions[i] == test_targets[i]:
            total_correct += 1
    print 'Accuracy w/ Decision Tree=' + str(total_correct / float(len(predictions)))

    cleanup_files()
