#! /usr/bin/python

import sys
import os
import requests
import json
import argparse
import webbrowser

CONFIG_DIR_PATH = os.path.join(os.path.expanduser('~'), '.gpm')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'config')

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
    parser.add_argument('-o', '--owner', action='append', help='the owner of the issue; pass multiple for a disjunction')
    parser.add_argument('-m', '--milestone', action='append', help='the milestone of the issue; pass multiple for a disjunction')
    #parser.add_argument('-l', '--labels', nargs='+', action='append', help='the labels on the issue; pass list for a conjunction; pass multiple for a disjunction')

    return parser

def save_config(config):
    if not os.path.isdir(CONFIG_DIR_PATH):
        os.makedirs(CONFIG_DIR_PATH)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config_file.write(json.dumps(config))
    return config

def load_config():
    try:
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            return json.loads(config_file.read())
    except IOError:
        config = {}
        save_config(config)
        return config

def cache_args_in_config(config, args):
    if args['token']:
        config['token'] = args['token']
    if args['user']:
        config['user'] = args['user']
    if args['repo']:
        config['repo'] = args['repo']
    return config

def cache_issues(config, issues):
    cache_dir = os.path.join(CONFIG_DIR_PATH, config['user'])
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    with open(os.path.join(cache_dir, config['repo']), 'w') as issue_cache:
        issue_cache.write(json.dumps(issues))

def load_issues(config):
    cache_file = os.path.join(CONFIG_DIR_PATH, config['user'], config['repo'])
    try:
        with open(cache_file, 'r') as issue_cache:
            return json.loads(issue_cache.read())
    except IOError:
        print "No issue cache, run with --fetch"
        sys.exit(-1)

def fetch_issues(config):
    print 'Fetching issues...'
    url = 'https://api.github.com/repos/' + config['user'] + '/' + config['repo'] + '/issues?state=open'
    issues = {}
    while url:
        if 'token' in config:
            r = requests.get(url, auth=(config['token'], 'x-oauth-basic'))
        else:
            r = requests.get(url)
        result = r.json()
        if 'message' in result:
            print result['message']
            sys.exit(-1)
        for issue in result:
            _issue = { 'owner': None, 'milestone': None}
            _issue['title'] = issue['title']
            if 'assignee' in issue and issue['assignee']:
                _issue['owner'] = issue['assignee']['login']
            if 'milestone' in issue and issue['milestone']:
                _issue['milestone'] = issue['milestone']['title']
            issues[issue['number']] = _issue
        if 'next' in r.links:
            url = r.links['next']['url']
        else:
            url = None
    print 'Successfully fetched ' + str(len(issues)) + ' issues'
    cache_issues(config, issues)
    return issues

def print_issues(issues):
    for issue in issues:
        number = issue
        issue = issues[number]
        print (number + ' ').rjust(5) + str(issue['title'][:100]).ljust(100) + ' [' + str(issue['owner']) + ', ' + str(issue['milestone']) + ']'

def browse_issues(issues, config):
    base_url = 'https://github.com/' + config['user'] + '/' + config['repo'] + '/issues/'
    for issue in issues:
        webbrowser.open_new_tab(base_url + str(issue))

def process_args(args):
    if args['owner']:
        args['owner'] = map(lambda x: x.lower(), args['owner'])
    if args['milestone']:
        args['milestone'] = map(lambda x: x.lower(), args['milestone'])
    return args

def in_args(value, arglist):
    value = str(value).lower()
    for arg in arglist:
        neg = False
        if arg[0] == '~':
            arg = arg[1:]
            neg = True
        found = value.find(arg) != -1
        if (not neg and found) or (neg and not found):
            return True
    return False

def filter_issues(issues, args):
    _issues = {}
    for issue in issues:
        number = issue
        issue = issues[number]
        if args['owner']:
            if not in_args(issue['owner'], args['owner']):
                continue
        if args['milestone']:
            if not in_args(issue['milestone'], args['milestone']):
                continue
        _issues[number] = issue
    return _issues

def main():
    args = process_args(vars(init_arg_parser().parse_args()))
    config = save_config(cache_args_in_config(load_config(), args))
    if 'user' not in config:
        print 'Please specify the user/org'
        sys.exit(-1)
    if 'repo' not in config:
        print 'Please specify the repo'
        sys.exit(-1)
    if args['fetch']:
        fetch_issues(config)
    issues = filter_issues(load_issues(config), args)
    if args['browser']:
        browse_issues(issues, config)
    else:
        print_issues(filter_issues(issues, args))
    print '* Found ' + str(len(issues)) + ' issues'

if __name__ == '__main__':
    main()
