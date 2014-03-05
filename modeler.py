import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

def main():
    with open('trained_and_cleansed.csv', 'r') as f:
        reader = csv.reader(f, quotechar='"')
        rows = [row for row in reader]  #Raw rows from the CSV file 

        labels, tweets = randomize_datasets(rows[1:])

        msgs_length = len(tweets) - 100

        #Vectorize our input based on the tf-idf algorithm
        vectorizer = TfidfVectorizer(input="content", ngram_range=(1, 3))   #Gonna feed it messages list; uni, bi & tri grams
        X = vectorizer.fit_transform(tweets[:-100])
        y = labels[:-100]

        #Create a logit regression classifier
        classifier = LogisticRegression(C=1e5)
        classifier.fit(X,y)

        '''
        We need to create a randomized list of messages so the training set 
        doesn't get accustomed to reading the data the same every time and
        overfitting the curve

        First, create indices list the size of messages and shuffle it.
        Then, shuffle the actual list
        '''

        #This is our test set
        x_test = vectorizer.transform(tweets[-100:])


        predictions = classifier.predict(x_test)
        print predictions
        print labels[-100:]

        count = 0
        for i in range(100):
            if predictions[i] == labels[-100+i]:
                count += 1
            print "Predicted: " + predictions[i] + " | Actual: " + labels[-100+i] 

        print "Total number correct out of 100: " + str(count)

'''
Randomly shuffle the given data set and return a tuple of (labels, tweets).

It is assumed that the dataset given is a list of lists of length 2.
The first index of each sub-list is assumed to be a label and the second
index is assumed to be a tweet (string)
'''
def randomize_datasets(dataset):
    np.random.seed(0)
    np.random.shuffle(dataset)

    labels = []
    messages = []

    for datum in dataset:
        #Datum[1] = Tweet, Datum[0] = Label
        messages.append(datum[1])
        labels.append(datum[0])

    return (labels, messages)

if __name__ == "__main__":
    main()