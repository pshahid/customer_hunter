import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import BernoulliRBM
import numpy as np

def main():
    with open('trained_and_cleansed.csv', 'r') as f:
        reader = csv.reader(f, quotechar='"')
        rows = [row for row in reader]  #Raw rows from the CSV file 

        labels, tweets = randomize_datasets(rows[1:])

        msgs_length = len(tweets) - 700

        #Vectorize our input based on the tf-idf algorithm
        vectorizer = TfidfVectorizer(input="content", ngram_range=(1, 3), min_df=5)   #Gonna feed it messages list; uni, bi & tri grams
        X = vectorizer.fit_transform(tweets[:-700])
        y = labels[:-700]

        '''
        We need to create a randomized list of messages so the training set 
        doesn't get accustomed to reading the data the same every time and
        overfitting the curve

        First, create indices list the size of messages and shuffle it.
        Then, shuffle the actual list
        '''
        # classifier = train_logit(X, y)
        classifier = train_sgd(X, y)        
        #This is our test set
        x_test = vectorizer.transform(tweets[-700:])


        predictions = classifier.predict(x_test)
        print predictions
        print labels[-700:]

        count = 0
        for i in range(700):
            if predictions[i] == labels[-700+i]:
                count += 1
            print "Predicted: " + predictions[i] + " | Actual: " + labels[-700+i] 

        print "Total number correct out of 700: " + str(count)

'''
Randomly shuffle the given data set and return a tuple of (labels, tweets).

It is assumed that the dataset given is a list of lists of length 2.
The first index of each sub-list is assumed to be a label and the second
index is assumed to be a tweet (string)
'''
def randomize_datasets(dataset):
    np.random.seed()
    np.random.shuffle(dataset)
    # print dataset
    labels = []
    messages = []

    for datum in dataset:
        #Datum[1] = Tweet, Datum[0] = Label
        messages.append(datum[1])
        labels.append(datum[0])

    return (labels, messages)

'''
Extract features from the data and return it as a numpy sparse matrix
'''
def extract(tweets):
    pass

'''
Given a classification algorithm train the data on the given labels and tweets
'''
def train(labels, tweets):
    pass

def test(labels, tweets):
    pass

def validate(filename):
    pass

'''
Train the data set on Logistic Regression.
'''
def train_logit(X, y):
    #Create a logit regression classifier
    classifier = LogisticRegression(C=1e5)
    classifier.fit_transform(X, y)

    return classifier

'''
Train the data set on stochastic gradient descent
'''
def train_sgd(X, y):
    #Hinge loss uses SVM, log uses logit regression
    classifier = SGDClassifier(loss='hinge', penalty='l2')
    classifier.fit_transform(X, y)

    return classifier

def train_binnb(X, y):
    pass


if __name__ == "__main__":
    main()