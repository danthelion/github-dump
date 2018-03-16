import argparse
import os
from pathlib import Path
from subprocess import Popen
from typing import Union, List, Tuple

import requests


def setup_dump_env(root: Union[str, None]) -> Path:
    dump_folder = Path(root if root else Path.home()) / 'gh-dump'
    if not dump_folder.exists():
        print(f'Creating directory: {dump_folder}')
        dump_folder.mkdir(exist_ok=True)
    else:
        exit(f'Target dump folder {dump_folder} already exists, aborting.')
    return dump_folder


def get_github_api_token() -> str:
    try:
        github_api_token = os.environ['GITHUB_API_TOKEN']
    except KeyError:
        github_api_token = input('`GITHUB_API_TOKEN` not found in environment, enter your access token: ')

    return github_api_token


def list_repos(user: str) -> List[Tuple[str, str]]:
    payload = {
        'access_token': get_github_api_token()
    }
    r = requests.get(f'https://api.github.com/users/{user}/repos?per_page=100', params=payload)
    return [(repo['name'], repo['ssh_url']) for repo in r.json()]


def _clone_repo_cmd(repo_url: str, dump_folder: Path) -> str:
    return f'git clone {repo_url} {dump_folder}'


def clone_repos(repos: List[Tuple[str, str]], dump_folder: Path) -> List[int]:
    proc = [Popen(_clone_repo_cmd(repo_url=repo[1], dump_folder=dump_folder / repo[0]), shell=True) for repo in repos]
    return [p.wait() for p in proc]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', help='GitHub username.', type=str, required=True)
    parser.add_argument(
        '--dump-root',
        help='A folder called `gh-dump` will be created to store the repo data in this folder.',
        type=str
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    gh_repos = list_repos(user=args.user)
    clone_repos(repos=gh_repos, dump_folder=setup_dump_env(root=args.dump_root))
