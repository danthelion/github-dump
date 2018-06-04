import argparse
import os
from pathlib import Path
from subprocess import Popen
from typing import List, Tuple

import requests


def setup_dump_env(root: Path) -> Path:
    """
    Create a folder to store the cloned repositories in.

    :param root: Full path to the parent folder of the dump folder.
    :return: Path to the dump folder.
    """
    dump_folder = root / 'gh-dump'
    if not dump_folder.exists():
        print(f'Creating folder: {dump_folder}')
        dump_folder.mkdir()
        return dump_folder
    else:
        exit(f'Target dump folder {dump_folder} already exists, aborting.')


def get_github_api_token() -> str:
    """
    Load the GitHub API access token from the environment or ask for it from the user.

    :return: Access token as a string.
    """
    try:
        return os.environ['GITHUB_API_TOKEN']
    except KeyError:
        return input('`GITHUB_API_TOKEN` not found in environment, enter your access token: ')


def list_repos(user: str) -> List[Tuple[str, str]]:
    """
    List repository names and ssh URLs for a user.

    :param user: GitHub username.
    :return: Repository names and SSH URLs as a list of tuples.
    """
    payload = {
        'access_token': get_github_api_token()
    }
    r = requests.get(f'https://api.github.com/users/{user}/repos?per_page=100', params=payload)
    return [(repo['name'], repo['ssh_url']) for repo in r.json()]


def _clone_repo_cmd(repo_url: str, dump_folder: Path) -> str:
    """
    Create a git command to clone a repository.

    :param repo_url: SSH URL of a repo.
    :param dump_folder: Target folder to clone into.
    :return: Formatted string ready to be run as a subprocess.
    """
    return f'git clone --mirror {repo_url} {dump_folder}'


def clone_repos(repos: List[Tuple[str, str]], dump_folder: Path) -> List[int]:
    """
    Clone repositories in subprocesses and wait for their results.

    :param repos: List of tuples containing a repos name and SSH URL.
    :param dump_folder:
    :return:
    """
    proc = [Popen(_clone_repo_cmd(repo_url=repo[1], dump_folder=dump_folder / repo[0]), shell=True) for repo in repos]
    return [p.wait() for p in proc]


def parse_args():
    """
    Parse CLI arguments.

    :return: Parsed argument namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', help='GitHub username.', type=str, required=True)
    parser.add_argument(
        '--dump-root',
        help='A folder called `gh-dump` will be created to store the repo data in this folder.',
        type=Path,
        default=Path.home()
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    clone_repos(repos=list_repos(user=args.user), dump_folder=setup_dump_env(root=args.dump_root))
