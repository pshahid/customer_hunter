import twitter
import sys


def main():
    print("Initializing the consumer...")
    api = twitter.Api(\
        consumer_key="s2amklHxL5CPIuJODNDo6g",\
        consumer_secret="vS74EYL9PsXTG3wWOlpoEREQmhcS9gKpIjJLWwHg",\
        access_token_key="125708842-bvfTWAHUwGqrd3LE5wDHCeuOxpHlGki7H4G4oEKb", 
        access_token_secret="rc8R5D6DJoIA7vj6Ubz1dPkt3tANLUBJ0xxEzdd2ORWg4")

    print("Verifying credentials.")
    user = api.VerifyCredentials()

    filters = [
        "att",
        "verizon",
        "tmobile",
        "t-mobile",
        "at&t"
    ]

    print("Filter set, creds verified, grabbing stream.")

    stream = api.GetStreamFilter(track=filters)

    try:
        tweet = None
        while True:
            tweet = stream.next()

            if tweet:
                if tweet["lang"] == "en":
                    print tweet
            else: 
                print("Tweet is none")
    except StopIteration:
        print("Stream can't move on.")
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected, exiting")

    sys.exit(0)

if __name__ == "__main__":
    main()