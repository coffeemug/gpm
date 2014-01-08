#! /usr/bin/python

import sys
import os
import requests
import json
import heapq

REPO=None
TOKEN=None
ISSUES=None

def print_basic_help():
    print 'List of commands:'
    print '\thelp\t\tPrint this help'
    print '\ttoken\t\tSet a token for repo access'
    print '\tadd\t\tAdd a repo'
    print '\tfetch\t\tFetch the latest set of issues'
    print '\tfilter\t\tFilter issues by various criteria'
    print 'Type `help COMMAND` for more information'

def print_init_help():
        print 'pm init GITHUB_USER/GITHUB_REPO [AUTH_TOKEN]\n'
        print """\tInitialize a new GitHub issues mirror in the current
\tdirectory (under `.p`) for the given GitHub repo"""

def print_fetch_help():
        print 'pm fetch\n'
        print """\tFetch the latest set of issues from GitHub"""

def print_filter_help():
        print 'pm filter\n'

        print """TODO"""

def cmd_help():
    # Too many arguments
    if len(sys.argv) > 3:
        print 'Unknown argument to `help`'
        print_basic_help()
        return
    # The user just wants some help
    if len(sys.argv) == 1 or len(sys.argv) == 2:
        print_basic_help()
        return
    # The user wants help for `help`
    if len(sys.argv) == 3 and sys.argv[2] == 'help':
        print_basic_help()
        return
    # The user wants help for `init`
    if len(sys.argv) == 3 and sys.argv[2] == 'init':
        print_init_help()
        return
    # The user wants help for `fetch`
    if len(sys.argv) == 3 and sys.argv[2] == 'fetch':
        print_fetch_help()
        return
    # The user wants help for `top`
    if len(sys.argv) == 3 and (sys.argv[2] == 'filter' or sys.argv[2] == 'f'):
        print_filter_help()
        return
    # We can't help the user
    print 'Unknown argument to `help`'
    print_basic_help()

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

def cmd_filter():
    setup_env()

def main():
    # Help
    if len(sys.argv) == 1 or sys.argv[1] == 'help' or sys.argv[1] == '--help':
        cmd_help()
        return
    # Init
    if sys.argv[1] == 'init':
        cmd_init()
        return
    # Fetch
    if sys.argv[1] == 'fetch':
        cmd_fetch()
        return
    # Top
    if sys.argv[1] == 'filter' or sys.argv[1] == 'f':
        cmd_filter()
        return
    print 'Unknown command'
    cmd_help()

if __name__ == '__main__':
    main()
