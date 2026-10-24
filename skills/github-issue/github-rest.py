#!/usr/bin/env python3
"""GitHub REST helper for the issue registry (see SKILL.md for usage).

This is a standard-library script that lives next to SKILL.md, not the `gh` CLI:
no `gh` binary is installed for this workflow and none is assumed. Invoke it by
path with `python3`; it is not executable and not on `PATH`.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path

API_BASE = 'https://api.github.com'
API_VERSION = '2022-11-28'
USER_AGENT = 'github-issue-skill/github-rest.py'
REQUEST_TIMEOUT = 30.0
RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 0.5
RETRY_JITTER = 0.5
RETRY_MAX_DELAY = 8.0
RETRY_MAX_AFTER = 60.0
METHODS = ('GET', 'POST', 'PATCH', 'PUT', 'DELETE')


class HelperError(RuntimeError):
    """A terminal, user-facing failure; `main` reports it and exits nonzero."""


def token_file() -> Path:
    """Operator token file, resolved per call so XDG_CONFIG_HOME stays overridable."""
    base = os.environ.get('XDG_CONFIG_HOME')
    config_dir = Path(base) if base else Path.home() / '.config'
    return config_dir / 'issue-pipeline' / 'github-token'


def _read_token_file(path: Path) -> str:
    """Read a plain token or an `AGENT_GH_TOKEN=...` line, without echoing it."""
    try:
        with open(path, encoding='utf-8') as fh:
            text = fh.read()
    except OSError:
        return ''
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith('#')
    ]
    for line in lines:
        if line.startswith('AGENT_GH_TOKEN='):
            return line.split('=', 1)[1].strip().strip('"\'')
    return lines[0] if len(lines) == 1 else ''


def resolve_token(slug: str) -> str:
    """Resolve the token without ever putting it in an error or a log line."""
    tok = os.environ.get('AGENT_GH_TOKEN')
    if tok:
        return tok
    tok = _read_token_file(token_file())
    if tok:
        return tok
    var = re.sub(r'[-.]', '_', slug.split('/')[-1]).upper() + '_GH_TOKEN'
    for name in (var, 'GH_TOKEN', 'GITHUB_TOKEN'):
        tok = os.environ.get(name)
        if tok:
            return tok
    return ''


def _repo_slug() -> str:
    """Derive owner/repo from `git remote get-url origin`."""
    try:
        completed = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
        )
    except OSError as err:
        raise HelperError(f'cannot run git: {err.strerror}') from err
    url = completed.stdout.strip()
    slug = re.sub(r'\.git$', '', re.sub(r'^(git@github\.com:|https://github\.com/)', '', url))
    if '/' not in slug:
        raise HelperError('cannot derive owner/repo from git remote origin')
    return slug


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Parse the command line; `--help` explains the method and payload rules."""
    parser = argparse.ArgumentParser(
        prog='github-rest.py',
        description=(
            'Call the GitHub REST API for the repository containing the current '
            'directory. This is a script from the github-issue skill, not the '
            '`gh` CLI.'
        ),
    )
    parser.add_argument('method', choices=METHODS, help='HTTP method')
    parser.add_argument('path', help='API path starting with /, for example /issues/42')
    parser.add_argument(
        'payload',
        nargs='?',
        help='JSON file sent verbatim, or a text file wrapped as {"body": <text>}',
    )
    return parser.parse_args(argv)


def _load_payload(path_text: str | None) -> str | None:
    """Build the request body from an optional JSON or text file."""
    if path_text is None:
        return None
    path = Path(path_text)
    try:
        text = path.read_text(encoding='utf-8')
    except OSError as err:
        raise HelperError(f'cannot read payload {path}: {err.strerror}') from err
    return text if path.suffix == '.json' else json.dumps({'body': text})


def _retry_after(err: urllib.error.HTTPError) -> int | None:
    """Delay from an integer `Retry-After` header; None when absent or an HTTP-date."""
    raw = err.headers.get('Retry-After') if err.headers is not None else None
    if raw is None:
        return None
    try:
        return max(0, int(raw))
    except ValueError:
        return None


def _sleep_backoff(attempt: int, retry_after: int | None) -> None:
    """Sleep before the next attempt: honored Retry-After, else jittered backoff."""
    if retry_after is not None:
        time.sleep(min(float(retry_after), RETRY_MAX_AFTER))
        return
    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_MAX_DELAY)
    time.sleep(delay + random.uniform(0.0, RETRY_JITTER))


def _http_error_message(err: urllib.error.HTTPError) -> str:
    """One-line error for a terminal HTTP status; the token lives only in headers."""
    try:
        payload = json.loads(err.read().decode('utf-8', errors='replace'))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return f'HTTP {err.code}: {err.reason}'
    message = payload.get('message') if isinstance(payload, dict) else None
    if isinstance(message, str) and message:
        return f'HTTP {err.code}: {message}'
    return f'HTTP {err.code}: {err.reason}'


def _request(
    slug: str,
    token: str,
    method: str,
    path: str,
    payload: str | None,
) -> bytes:
    """Send one request with bounded transient retry; return the response body.

    Transient (retried up to RETRY_ATTEMPTS): transport-level failures
    (URLError, timeouts, dropped connections) and HTTP 5xx; on 429 an integer
    Retry-After is honored, capped at RETRY_MAX_AFTER. Every other status —
    including a native 404 — is a terminal answer, never retried.
    """
    req = urllib.request.Request(
        API_BASE + '/repos/' + slug + path,
        data=payload.encode('utf-8') if payload is not None else None,
        headers={
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.github+json',
            'User-Agent': USER_AGENT,
            'X-GitHub-Api-Version': API_VERSION,
        },
        method=method,
    )
    attempt = 0
    while True:
        try:
            resp = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
            try:
                return resp.read()
            finally:
                resp.close()
        except urllib.error.HTTPError as err:
            transient = err.code == 429 or err.code >= 500
            if not transient:
                raise HelperError(_http_error_message(err)) from err
            if attempt + 1 >= RETRY_ATTEMPTS:
                raise HelperError(
                    f'HTTP {err.code} persists after {RETRY_ATTEMPTS} attempts'
                ) from err
            _sleep_backoff(attempt, _retry_after(err))
            attempt += 1
        except (OSError, http.client.HTTPException) as err:
            if attempt + 1 >= RETRY_ATTEMPTS:
                raise HelperError(
                    f'network error persists after {RETRY_ATTEMPTS} attempts: {err}'
                ) from err
            _sleep_backoff(attempt, None)
            attempt += 1


def _decode_json(body: bytes) -> object | None:
    """Decode a response body; an empty body decodes to None."""
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError as err:
        raise HelperError(f'invalid JSON response: {err.msg}') from err


def _print_result(method: str, body: bytes) -> None:
    """Print the useful part of a response: the JSON body, a URL or `done`."""
    if method == 'DELETE':
        print('done')
        return
    data = _decode_json(body)
    if method == 'GET':
        if data is not None:
            print(json.dumps(data, indent=2))
        return
    url = data.get('html_url') if isinstance(data, dict) else None
    print(url if isinstance(url, str) else 'ok')


def main(argv: Sequence[str] | None = None) -> int:
    """Run one GitHub call; return 0 on success and 1 on a terminal failure."""
    args = _parse_args(argv)
    try:
        slug = _repo_slug()
        token = resolve_token(slug)
        if not token:
            raise HelperError(
                f'no token: set AGENT_GH_TOKEN, write {token_file()} (one line, '
                'chmod 600), set the per-repository <REPO>_GH_TOKEN, or set '
                'GH_TOKEN/GITHUB_TOKEN'
            )
        payload = _load_payload(args.payload)
        body = _request(slug, token, args.method, args.path, payload)
    except HelperError as err:
        print(err, file=sys.stderr)
        return 1
    _print_result(args.method, body)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
