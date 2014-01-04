#! /usr/bin/python

import sys
import os
import requests
import json
import heapq

REPO=None
ISSUES=None
CMPS=None
TOKEN=None

def print_basic_help():
    print 'List of commands:'
    print '\thelp\t\tPrint this help'
    print '\tinit\t\tInitialize a new priority queue for a GitHub repo'
    print '\tfetch\t\tFetch the latest set of issues'
    print '\ttop\t\tPrint the most important issues'
    print 'Type `help COMMAND` for more information'

def print_init_help():
        print 'p init GITHUB_USER/GITHUB_REPO [AUTH_TOKEN]\n'
        print """\tInitialize a new priority queue in the current
\tdirectory (under `.p`) for the given GitHub repo"""

def print_fetch_help():
        print 'p fetch\n'
        print """\tFetch the latest set of issues from GitHub"""

def print_top_help():
        print 'p top\n'

        print """\tPrint top 10 most important issues. Might require interactive
\trating if not enough issues are rated to generate the top list"""

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
    if len(sys.argv) == 3 and sys.argv[2] == 'top':
        print_top_help()
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
        with open('cmp_cache', 'w') as cmp_cache:
            cmp_cache.write(json.dumps([]))
        with open('token', 'w') as token:
            if len(sys.argv) == 4:
                token.write(sys.argv[3])
        with open('.gitignore', 'w') as ignore:
            ignore.write('token\n')
            ignore.write('issue_cache\n')
    except:
        print "Can't initialize the priority queue. Does one already exist?"
        return

    print """Successfully initialized the priority queue. Now run `p fetch` to
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
        with open('cmp_cache', 'r') as cmp_cache:
            global CMPS
            CMPS = {}
            cmps = json.loads(cmp_cache.read())
            for _cmp in cmps:
                CMPS[tuple(_cmp[0])] = _cmp[1]
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

def cache_store(i1, i2, c):
    global CMPS
    if i1.number > i2.number:
        temp = i1
        i1 = i2
        i2 = temp
        c *= -1
    CMPS[(i1.number, i2.number)] = c
    # now dump it
    cmps = []
    for _cmp in CMPS:
        cmps.append([list(_cmp), CMPS[_cmp]])
    with open('cmp_cache', 'w') as cmp_cache:
        cmp_cache.write(json.dumps(cmps))

def cache_lt(i1, i2):
    global CMPS
    if i1.number > i2.number:
        temp = i1
        i1 = i2
        i2 = temp
        return CMPS[(i1.number, i2.number)] == 1
    else:
        return CMPS[(i1.number, i2.number)] == -1

def maybe_interactive_lt(i1, i2):
    # Try a look up first
    try:
        return cache_lt(i1, i2)
    except:
        pass
    # Couldn't look it up :(
    while True:
        print "Please pick which issue is more import:"
        print "[1]: #" + str(i1.number) + " - " + ISSUES[i1.number]
        print "[2]: #" + str(i2.number) + " - " + ISSUES[i2.number]
        sys.stdout.write("12=[]fq?: ")
        res = sys.stdin.readline()
        print
        if res == '':
            sys.exit(0)
        elif res[0] == 'q':
            sys.exit(0)
        elif res[0] == '1':
            cache_store(i1, i2, -1)
            return True
        elif res[0] == '2':
            cache_store(i1, i2, 1)
            return False
        elif res[0] == '=':
            cache_store(i1, i2, 0)
            return i1.number < i2.number
        elif res[0] == '[':
            pass
        elif res[0] == ']':
            pass
        elif res[0] == 'f':
            pass
        elif res[0] == '?':
            print """1 - the first issue is more import
2 - the second issue is more important
= - both issues are equally important
[ - forget the left issue (always treat it as unimportant)
] - forget the right issue (always treat it as unimportant)
f - forget both issues (always treat them as unimportant)
q - quit
? - print this help
"""
        else:
            sys.stdout.write("This is hard enough without bad input. ")

class Issue:
    def __init__(self, number):
        self.number = number
    def __lt__(self, other):
        return maybe_interactive_lt(self, other)

def cmd_top():
    setup_env()
    global ISSUES
    issues = []
    for issue in ISSUES:
        issues.append(Issue(issue))
    k = 10
    smallest = heapq.nsmallest(k, issues)
    for i in xrange(0, k):
        print "[" + str(i + 1) + "]: #" + str(smallest[i].number) + " - " + ISSUES[smallest[i].number]

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
    if sys.argv[1] == 'top':
        cmd_top()
        return
    print 'Unknown command'
    cmd_help()

if __name__ == '__main__':
    main()
