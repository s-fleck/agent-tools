#!/usr/bin/env python3
"""GitHub REST helper for this project's repo (see SKILL.md for usage)."""
import json, os, re, subprocess, sys, urllib.request

method, path, *rest = sys.argv[1:]
slug = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
slug = re.sub(r'\.git$', '', re.sub(r'^(git@github\.com:|https://github\.com/)', '', slug))
if '/' not in slug:
    sys.exit('cannot derive owner/repo from git remote origin')
var = re.sub(r'[-.]', '_', slug.split('/')[-1]).upper() + '_GH_TOKEN'
try:
    env = open(os.path.expanduser('~/.Renviron')).read()
except OSError:
    env = ''
m = re.search(rf'^{var}=(\S+)', env, re.M)
tok = ((m.group(1).strip('"\'') if m else '') or os.environ.get('GH_TOKEN')
       or os.environ.get('GITHUB_TOKEN'))
if not tok:
    sys.exit(f'no token: set {var} in ~/.Renviron or GH_TOKEN')
payload = None
if rest:
    text = open(rest[0]).read()
    payload = text.encode() if rest[0].endswith('.json') else json.dumps({'body': text}).encode()
req = urllib.request.Request(
    'https://api.github.com/repos/' + slug + path, data=payload,
    headers={'Authorization': 'Bearer ' + tok, 'Accept': 'application/vnd.github+json'},
    method=method)
resp = urllib.request.urlopen(req)
if method == 'DELETE':
    print('done')
else:
    data = json.load(resp)
    print(json.dumps(data, indent=2) if method == 'GET' else data.get('html_url', 'ok'))
