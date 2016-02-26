from collections import Counter
import re
import operator

from nltk import word_tokenize

from Scrapper import read_debates_from_file

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
    with open(filename, mode='a') as output_file:
        for line in lines:
            output_file.write(line)
            output_file.write('\n')


def set_up_train_and_test_files():
    """
    Adds data to train and test files,
    that conforms to the SVM_Light
    :return:
    """
    debates = read_debates_from_file('abortion_debates.txt')

    con_data_dict = {}
    pro_data_dict = {}

    max_con_value = 1
    max_pro_value = 1

    lines = []
    j = 1
    for debate in list(debates)[:-2000]:
        for round in debate.rounds:
            svm_pro_line = '1'
            svm_con_line = '-1'

            # Prep pro data for SVM_Light
            for word in word_tokenize(round.pro_data):
                word = word.lower()
                for i in chars:
                    word = word.replace(i, '')
                for i in positions:
                    word = word.replace(i, '')
                if word.isdigit() \
                        or re.compile('www.*').match(word) is not None:
                    continue
                if word not in pro_data_dict:
                    pro_data_dict[word] = max_pro_value
                    max_pro_value += 1
            counter = Counter(word_tokenize(round.pro_data))

            for k, v in sorted(pro_data_dict.items(), key=operator.itemgetter(1)):
                if counter[k] != 0:
                    svm_pro_line += ' ' + str(pro_data_dict[k]) + ':' + str(counter[k] / float(len(round.pro_data)))

            # Prep con data for SVM_Light
            for word in word_tokenize(round.con_data):
                word = word.lower()
                for i in chars:
                    word = word.replace(i, '')
                for i in positions:
                    word = word.replace(i, '')
                if word.replace('.', '').isdigit() \
                        or re.compile('www.*').match(word) is not None:
                    continue
                if word not in con_data_dict:
                    con_data_dict[word] = max_con_value
                    max_con_value += 1
            counter = Counter(word_tokenize(round.con_data))

            for k, v in sorted(con_data_dict.items(), key=operator.itemgetter(1)):
                if counter[k] != 0:
                    svm_con_line += ' ' + str(con_data_dict[k]) + ':' + str(counter[k] / float(len(round.con_data)))

            print j
            j += 1
            # print svm_con_line
            # print svm_pro_line

            lines.append(svm_con_line)
            lines.append(svm_pro_line)
    write_lines_to_file('train.data', lines)


if __name__ == "__main__":
    set_up_train_and_test_files()
