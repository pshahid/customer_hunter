import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

def main():
    with open('trained_and_cleansed.csv', 'r') as f:
        reader = csv.reader(f, quotechar='"')
        rows = [row for row in reader]  #Raw rows from the CSV file 
        messages = [row[1] for row in rows[1:]] # All of the tweets (ignore the header using [1:])
        labels = [row[0] for row in rows[1:]]   # Either 1 or 0
        msgs_length = len(messages) - 100

        #Create indices list the size of the messages list & randomize them
        indices = [i for i in range(msgs_length)]
        new_messages = []   #These messages will be shuffled
        linked_labels = []  #These labels will be shuffled
        np.random.shuffle(indices)

        for index in indices:
            new_messages.append(messages[index])
            linked_labels.append(labels[index])

        #Vectorize our input based on the tf-idf algorithm
        vectorizer = TfidfVectorizer(input="content", ngram_range=(1, 3))   #Gonna feed it messages list; uni, bi & tri grams
        X = vectorizer.fit_transform(new_messages[:-100])
        y = linked_labels[:-100]

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
        x_test = vectorizer.transform(new_messages[-100:])


        predictions = classifier.predict(x_test)
        print predictions
        print linked_labels[-100:]

        count = 0
        for i in range(100):
            if predictions[i] == linked_labels[-100+i]:
                count += 1
            print "Predicted: " + predictions[i] + " | Actual: " + linked_labels[-100+i] 

        print "Total number correct out of 100: " + str(count)

if __name__ == "__main__":
    main()