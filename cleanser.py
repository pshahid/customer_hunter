import re
import csv

def main():
    matchexpr = "\\n[^((1|0)\\,)]"
    rows = []
    with open('trained_tweets.csv', 'r') as f:
        reader = csv.reader(f, quotechar='"')

        for row in reader:
            rows.append(row)

    with open('trained_and_cleansed.csv', 'w') as f:

        writer = csv.writer(f, quotechar='"')
        for row in rows:
            tmp = row[1]
            tmp = tmp.replace('\r\n', '')
            tmp = tmp.replace('\n', '')
            tmp = tmp.replace('\r', '')
            tmp = tmp.replace('&lt;', '<')
            tmp = tmp.replace('&gt;', '>')
            tmp = tmp.replace('&amp;', '&')
            tmp = tmp.replace('&quot;', '"')
            tmp = tmp.replace('&#39;', "'")
            tmp = tmp.replace('&#039;', "'")
            row[1] = tmp
            writer.writerow(row)


if __name__ == "__main__":
    main()