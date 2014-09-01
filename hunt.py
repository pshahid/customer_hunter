#!/usr/local/bin/python

import argparse
import subprocess


def start_twitter(production):
    import jobs.twitterjob as twitter
    print "Twitter job started."

    if production:
        print "Production is true"

    twitter.start()

def start_insta(production):
    print "Instagram job started."

    if production:
        print "Production is true"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Main customer hunter file.")

    parser.add_argument('-c', '--collect', choices=['t', 'i'])
    parser.add_argument('-p', '--production', action='store_true')

    args = parser.parse_args()

    if args.collect == 't':
        start_twitter(args.production)

    if args.collect == 'i':
        start_insta(args.production)

    print args