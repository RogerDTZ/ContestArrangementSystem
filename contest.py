import os
import re
import sys
from pathlib import Path
from util import *


class Contest:
    path: Path
    title: str
    team_category_id: int
    team_id_range: tuple
    lock: bool

    def __init__(self, path, title, team_category_id, team_id_range, lock):
        self.path = path
        self.title = title
        self.team_category_id = team_category_id
        self.team_id_range = team_id_range
        self.lock = lock

    def write(self):
        write_yaml(self.path / 'contest.yaml', {
            'title': self.title,
            'team_category_id': self.team_category_id,
            'team_id_range': '{}-{}'.format(self.team_id_range[0], self.team_id_range[1]),
            'lock': self.lock
        })

    def toggle_lock(self, lock: bool):
        self.lock = lock
        self.write()


def is_contest_directory(path):
    return (path / 'contest.yaml').is_file()


def get_contest(path=Path('.')):
    if not is_contest_directory(path):
        error('Is this a contest directory? contest.yaml not found.')
    data = read_yaml(path / 'contest.yaml')
    return Contest(
        path,
        data['title'],
        int(data['team_category_id']),
        decode_range(data['team_id_range'], 'team_id_rage'),
        bool(data['lock'])
    )


def create_contest():
    title = ask_variable('contest name')
    dirname = ask_variable('directory name')
    if Path(dirname).is_dir():
        error('directory {} exists.'.format(dirname))
    team_category_id = int(ask_variable('team category id'))
    team_id_range = decode_range(ask_variable('team id range').strip(), 'team_id_range')

    path = Path('.') / dirname
    path.mkdir()
    contest = Contest(path, title, team_category_id, team_id_range, False)
    contest.write()


def toggle_lock(lock):
    if not is_contest_directory(Path('.')):
        error('Is this a contest directory? contest.yaml not found.')
    contest = get_contest()
    contest.toggle_lock(lock)
    contest.write()


