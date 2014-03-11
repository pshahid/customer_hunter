import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import BernoulliRBM
import numpy as np

class Modeler(object):
    def __init__(self, training, test):
        self.training_file = training
        self.test_file = test

        self.trained_logit = None
        self.trained_sgd = None
        self.vectorizer = None
        np.random.seed()

    def predict(self, text):
        text_vector = self.vectorizer.transform(text)

        logit = self.trained_logit.predict(text_vector)
        sgd = self.trained_sgd.predict(text_vector)

        return {'logit': logit, 'sgd': sgd}

    def load_training(self):
        labels = None
        texts = None
        sniffer = csv.Sniffer()

        with open(self.training_file, 'r') as training_file:
            reader = csv.reader(training_file, quotechar='"')
            rows = [row for row in reader][0:]

            labels, texts = self._randomize_dataset(rows)
        #File gets closed here

        self.vectorizer = TfidfVectorizer(input="content", ngram_range=(1, 3), min_df=5)
        X = self.vectorizer.fit_transform(texts)
        y = labels

        self.trained_logit = self._train_logit(X, y)
        self.trained_sgd = self._train_sgd(X, y)

    def load_test(self):
        test_labels = None
        test_texts = None

        with open(self.test_file, 'r') as test_file:
            test_reader = csv.reader(test_file, quotechar='"')
            test_rows = [row for row in test_reader][0:]

            test_labels, test_texts = self._randomize_dataset(test_rows)

        x_test = self.vectorizer.transform(test_texts)

        logit_predictions = self._test_logit(x_test)
        sgd_predictions = self._test_sgd(x_test)
        
        everything = zip(test_labels, logit_predictions, sgd_predictions)
        
        total_rows = len(everything)
        correct_logit = 0
        correct_sgd = 0

        for prediction in everything:
            if prediction[1] == prediction[0]:
                correct_logit += 1

            if prediction[2] == prediction[0]:
                correct_sgd += 1

        pct_logit = 100 * (float(correct_logit) / float(total_rows))
        pct_sgd = 100 * (float(correct_sgd) / float(total_rows))

        return (pct_logit, pct_sgd)
        
    def _test_logit(self, test):
        return self.trained_logit.predict(test)

    def _test_sgd(self, test):
        return self.trained_sgd.predict(test)

    def _train_logit(self, X, y):
        classifier = LogisticRegression(C=1e5)
        classifier.fit_transform(X, y)

        return classifier

    def _train_sgd(self, X, y):
        classifier = SGDClassifier(loss='hinge', penalty='l2')
        classifier.fit_transform(X, y)

        return classifier      

    def _randomize_dataset(self, dataset):
        np.random.shuffle(dataset)
        # print dataset
        labels = []
        messages = []

        for datum in dataset:
            #Datum[1] = Tweet, Datum[0] = Label
            messages.append(datum[1])
            labels.append(datum[0])

        return (labels, messages)
