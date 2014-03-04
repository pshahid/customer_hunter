import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def main():
    with open('trained_and_cleansed.csv', 'r') as f:
        reader = csv.reader(f, quotechar='"')
        rows = [row for row in reader]  #Raw rows from the CSV file 
        messages = [row[1] for row in rows[1:]] # All of the tweets (ignore the header using [1:])
        labels = [row[0] for row in rows[1:]]   # Either 1 or 0

        vectorizer = TfidfVectorizer(input="content", ngram_range=(1, 3))   #Gonna feed it messages list; uni, bi & tri grams
        X = vectorizer.fit_transform(messages[:-100])
        y = labels[:-100]

        # print X

        classifier = LogisticRegression(C=1e5)
        classifier.fit(X,y)

        x_test = vectorizer.transform(messages[-100:])

        predictions = classifier.predict(x_test)
        print predictions
        print labels[-100:]

        count = 0
        for i in range(100):
            if predictions[i] == labels[-100+i]:
                count += 1
            print "Predicted: " + predictions[i] + " | Actual: " + labels[-100+i] 

        print "Total number correct out of 100: " + str(count)

if __name__ == "__main__":
    main()