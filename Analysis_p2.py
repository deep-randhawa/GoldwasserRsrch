# Imports
from optparse import OptionParser

from sklearn import svm, tree
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2, f_classif

from Util import *

op = OptionParser()
op.add_option("--chi2_select",
              action="store", type="int", dest="select_chi2",
              help="Select some number of features using a chi-squared test")
op.add_option("--top10",
              action="store_true", dest="print_top10",
              help="Print ten most discriminative terms per class"
                   " for every classifier.")
op.add_option("--n_features",
              action="store", type=int, default=2 ** 16,
              help="n_features when using the tfidf vectorizer.")


# Getting data
print 'Getting corpus'
all_debates = list(read_debates_from_file('abortion_debates.txt'))
corpus_pro = [y.pro_data for x in all_debates for y in x.rounds]
corpus_con = [y.con_data for x in all_debates for y in x.rounds]

corpus = corpus_pro + corpus_con
targets = [1] * len(corpus_pro) + [0] * len(corpus_con)

# Shuffling corpus and targets
tmp_ct = list(zip(corpus, targets))
random.shuffle(tmp_ct)
corpus, targets = zip(*tmp_ct)

print 'Vectorizing corpus'
vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
X = corpus
y = targets

assert len(X) == len(y)

split_at = int(len(X) * 0.75)
X_train, X_test = X[:split_at], X[split_at:]
y_train, y_test = y[:split_at], y[split_at:]

X_train = vectorizer.fit_transform(X_train)
X_test = vectorizer.transform(X_test)

# Selecting the best features
print 'Running feature selection'
v2 = SelectKBest(f_classif, k=1000)
X_train = v2.fit_transform(X_train, y_train)
X_test = v2.transform(X_test)

split = int(len(X) * 0.75)
train_features, train_targets = X[:split], y[:split]
test_features, test_targets = X[split + 1:], y[split + 1:]

print 'Testing on data w/ SVM ...'
clf = svm.SVC()
clf.fit(X_train, y_train)
print '\tAccuracy: ' + str(clf.score(X_test, y_test))

print 'Testing on data w/ Decision Trees'
clftree = tree.DecisionTreeClassifier()
clftree = clftree.fit(X_train, y_train)
print '\tAccuracy: ' + str(clftree.score(X_test, y_test))
