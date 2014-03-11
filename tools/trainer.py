import csv

def main():
    with open("tweet_test.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, quotechar='"')
        rows = []
        for row in reader:
            rows.append(row)

    with open("trained_tweets.csv", "w") as csvfile:
        writer = csv.writer(csvfile, quotechar='"')
        writer.writerow(["negative", "message"])
        for row in rows[1:]:
            print row[1]
            print "[Hit enter for 0]",
            row[0] = raw_input()

            if row[0] == "":
                row[0] = '0'

            while row[0] not in ('0', '1', 0, 1, ""):
                print "Please input correct input"
                row[0] = raw_input()

                if row[0] == "":
                    row[0] = "0"

            print "Input registered: [" + str(row[0]) + "] \n"
            writer.writerow(row)

if __name__ == "__main__":
    main()