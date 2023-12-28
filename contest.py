from util import *
import affiliation
import contestant
import seat
from colorama import Fore


class Contest:
    path: Path
    title: str
    team_category_ids: list[int]
    team_id_range: tuple
    account_prefix: str
    lock: bool
    teamid_pool: set

    def __init__(self, path, title, team_category_ids, team_id_range, account_prefix, lock):
        self.path = path
        self.title = title
        self.team_category_ids = team_category_ids
        self.team_id_range = team_id_range
        self.teamid_pool = set(range(self.team_id_range[0], self.team_id_range[1] + 1))
        self.account_prefix = account_prefix
        self.lock = lock

    def write(self):
        write_yaml(self.path / 'contest.yaml', {
            'title': self.title,
            'team_category_ids': ",".join(map(str, self.team_category_ids)),
            'team_id_range': '{}-{}'.format(self.team_id_range[0], self.team_id_range[1]),
            'account_prefix': self.account_prefix,
            'lock': self.lock,
        })

    def toggle_lock(self, lock: bool):
        self.lock = lock
        self.write()

    def locked(self):
        return self.lock, (Fore.GREEN + '[Locked]' if self.lock else Fore.YELLOW + '[Unlocked]') + Fore.RESET

    def get_capacity(self):
        return min(self.team_id_range[1] - self.team_id_range[0] + 1, seat.get_seats_num())

    def get_available_teamid(self):
        if len(self.teamid_pool) == 0:
            error('No available team id.')
        return min(self.teamid_pool)

    def occupy_teamid(self, team_id):
        if team_id not in self.teamid_pool:
            return False
        self.teamid_pool.remove(team_id)
        return True

    def release_teamid(self, team_id):
        if team_id < self.team_id_range[0] or team_id > self.team_id_range[1]:
            error('Team id {} is not in the valid range.'.format(team_id))
        if team_id in self.teamid_pool:
            error('Unexpected: team id {} is already available.'.format(team_id))
        self.teamid_pool.add(team_id)

    def print(self):
        print("""
 title:               {}
 lock state:          {}
 team_category ids:   {}
 team_id range:       {}
 account_prefix:      {}
 affiliation:         {}
 room:                {}
 available seats:     {}
 capacity:            {}
 seat state:          {}
 password state:      {}
 contest state:       {}
        """.format(
            self.title,
            self.locked()[1],
            ", ".join(map(str, self.team_category_ids)),
            '{} ~ {}'.format(self.team_id_range[0], self.team_id_range[1]),
            self.account_prefix,
            affiliation.get_affiliations_num(),
            seat.get_room_info(),
            seat.get_seats_num(),
            '[{} / {}]'.format(contestant.get_contestants_num(), self.get_capacity()),
            contestant.get_contestant_seat_state()[1],
            contestant.get_contestant_password_state()[1],
            get_ready_state()[1]
        ))


g_contest = None


def is_contest_directory(path=Path('.')):
    return (path / 'contest.yaml').is_file()


def ensure_contest_directory(path=Path('.')):
    if not is_contest_directory(path):
        error('Is this a contest directory? contest.yaml not found.')


def get_contest():
    global g_contest

    if g_contest is not None:
        return g_contest

    path = Path('.')
    ensure_contest_directory(path)
    data = read_yaml(path / 'contest.yaml')
    g_contest = Contest(
        path=path,
        title=data['title'],
        team_category_ids=list(map(int, data['team_category_ids'].strip().split(','))),
        team_id_range=decode_range(data['team_id_range'], 'team_id_rage'),
        account_prefix=data['account_prefix'],
        lock=bool(data['lock'])
    )
    return g_contest


def create_contest():
    title = ask_variable('contest name')
    dirname = ask_variable('directory name')
    if Path(dirname).is_dir():
        error('directory {} exists.'.format(dirname))
    team_category_ids = list(map(int, ask_variable('team category ids (split by \',\', no space)').strip().split(',')))
    team_id_range = decode_range(ask_variable('team id range').strip(), 'team_id_range')
    account_prefix = ask_variable('account prefix').strip().replace(' ', '_')

    root_path = Path('.') / dirname
    root_path.mkdir()
    path = root_path / 'data'
    path.mkdir()

    path = (root_path / 'data' / 'contestants.json')
    if not path.is_file():
        with open(path, 'w', encoding='utf-8') as f:
            f.write('[]\n')
    path = (root_path / 'data' / 'seats.tsv')
    if not path.is_file():
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
    path = (root_path / 'data' / 'affiliations.tsv')
    if not path.is_file():
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')

    contest = Contest(path=root_path, title=title, team_category_ids=team_category_ids, team_id_range=team_id_range, account_prefix=account_prefix, lock=False)
    contest.write()


def toggle_lock(lock):
    ensure_contest_directory()
    contest = get_contest()
    if lock != contest.lock:
        if not lock:
            if ask_variable('Are you sure? (y/n)', 'n')[0] not in ['y', 'Y']:
                user_abort()
        contest.toggle_lock(lock)
        contest.write()
    contest.print()


def contest_locked():
    return get_contest().locked()


def get_capacity():
    return get_contest().get_capacity()


def contest_full():
    return contestant.get_contestants_num() == get_contest().get_capacity()

def valid_team_category(cat):
    return cat in get_contest().team_category_ids

def occupy_teamid(team_id):
    return get_contest().occupy_teamid(team_id)


def release_teamid(team_id):
    return get_contest().release_teamid(team_id)


def get_available_teamid():
    return get_contest().get_available_teamid()


def get_ready_state():
    ready = Fore.GREEN + '[Ready]' + Fore.RESET
    not_ready = Fore.RED + '[Not Ready]' + Fore.RESET
    flag = True
    problem = list()
    if not contestant.get_contestant_seat_state()[0]:
        flag = False
        problem.append('seat')
    if not contestant.get_contestant_password_state()[0]:
        flag = False
        problem.append('password')
    if not contest_locked()[0]:
        flag = False
        problem.append('lock')
    return flag, ready if flag else not_ready + ' (issue: ' + ', '.join(problem) + ')'


