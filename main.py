#! /usr/bin/python

import sys
import os
import requests
import json
import argparse

USER=None
REPO=None
TOKEN=None
ISSUES=None

def cmd_init():
    # Too many arguments
    if len(sys.argv) > 4:
        print 'Unknown argument to `init`'
        print_init_help()
        return
    # Too few arguments
    if len(sys.argv) < 3:
        print 'Too few arguments to `init`'
        print_init_help()
        return
    try:
        os.makedirs('.p')
        os.chdir('.p')
        with open('repo', 'w') as repo:
            repo.write(sys.argv[2])
            repo.write('\n')
        with open('issue_cache', 'w') as issue_cache:
            issue_cache.write(json.dumps({}))
        with open('token', 'w') as token:
            if len(sys.argv) == 4:
                token.write(sys.argv[3])
        with open('.gitignore', 'w') as ignore:
            ignore.write('token\n')
            ignore.write('issue_cache\n')
    except:
        print "Can't initialize the priority queue. Does one already exist?"
        return

    print """Successfully initialized the priority queue. Now run `pm fetch` to
fetch latest issues"""

def setup_env(last_dir=None):
    if last_dir == os.getcwd():
        print "Can't find priority queue"
        return
    if os.path.isdir('.p'):
        os.chdir('.p')
        with open('repo', 'r') as repo:
            global REPO
            REPO = repo.readline().strip()
        with open('issue_cache', 'r') as issue_cache:
            global ISSUES
            ISSUES = {}
            issues = json.loads(issue_cache.read())
            for issue in issues:
                ISSUES[int(issue)] = issues[issue]
        with open('token', 'r') as token:
            global TOKEN
            TOKEN = token.readline().strip()
    else:
        cwd = os.getcwd()
        os.chdir('..')
        setup_env(last_dir=cwd)

def cmd_fetch():
    setup_env()
    global REPO
    global ISSUES
    global TOKEN
    url = 'https://api.github.com/repos/' + REPO + '/issues?state=open'
    new_issues = {}
    while url:
        if TOKEN:
            r = requests.get(url, auth=(TOKEN, 'x-oauth-basic'))
        else:
            r = requests.get(url)
        for issue in r.json():
            new_issues[issue['number']] = issue['title']
        if 'next' in r.links:
            url = r.links['next']['url']
        else:
            url = None
    count = len(new_issues)
    new_count = len(set(new_issues) - set(ISSUES))
    closed_count = len(set(ISSUES) - set(new_issues))
    ISSUES = new_issues
    with open('issue_cache', 'w') as issue_cache:
        issue_cache.write(json.dumps(ISSUES))
    print 'Successfully fetched ' + str(count) + ' issues, ' + str(new_count) + ' updated, ' + str(closed_count) + ' closed'

def init_arg_parser():
    parser = argparse.ArgumentParser(description='Query github issues.')
    ## Basic access configuration
    parser.add_argument('-t', '--token', help='a github token to use (cached)')
    parser.add_argument('-u', '--user', help='a github user or organization to use (cached)')
    parser.add_argument('-r', '--repo', help='a github repo to use (cached)')
    ## Additional controls
    parser.add_argument('-f', '--fetch', action='store_true', help='fetch updates from github')
    parser.add_argument('-b', '--browser', action='store_true', help='open issue list in the browser')
    ## Filters
    parser.add_argument('-s', '--status', choices=['open', 'closed', 'all'], default='open', help='which issues to show (defaults to open)')
    parser.add_argument('-o', '--owner', action='append', help='the owner of the issue; pass multiple for a disjunction')
    parser.add_argument('-m', '--milestone', action='append', help='the milestone of the issue; pass multiple for a disjunction')
    #parser.add_argument('-l', '--labels', nargs='+', action='append', help='the labels on the issue; pass list for a conjunction; pass multiple for a disjunction')

    return parser

def main():
    args = init_arg_parser().parse_args()
    print args

if __name__ == '__main__':
    main()
