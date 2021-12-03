from util import *
import contestant
import seat


class Contest:
    path: Path
    title: str
    team_category_id: int
    team_id_range: tuple
    lock: bool
    teamid_pool: set
    capacity: int

    def __init__(self, path, title, team_category_id, team_id_range, lock):
        self.path = path
        self.title = title
        self.team_category_id = team_category_id
        self.team_id_range = team_id_range
        self.teamid_pool = set(range(self.team_id_range[0], self.team_id_range[1] + 1))
        self.capacity = min(len(self.teamid_pool), seat.get_seats_num())
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

    def locked(self):
        return self.lock

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
 lock state:          [{}]
 team_category id:    {}
 team_id range:       {}
 room:                {}
 available seats:     {}
 capacity:            {}
        """.format(
            self.title,
            'locked' if self.lock else 'unlocked',
            self.team_category_id,
            '{} ~ {}'.format(self.team_id_range[0], self.team_id_range[1]),
            seat.get_room_info(),
            seat.get_seats_num(),
            '{} / {}'.format(contestant.get_contestants_num(), self.capacity),
        ))
        # TODO: add affiliation information


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
        path,
        data['title'],
        int(data['team_category_id']),
        decode_range(data['team_id_range'], 'team_id_rage'),
        bool(data['lock'])
    )
    return g_contest


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
    return get_contest().capacity


def contest_full():
    return contestant.get_contestants_num() == get_contest().capacity


def occupy_teamid(team_id):
    return get_contest().occupy_teamid(team_id)


def release_teamid(team_id):
    return get_contest().release_teamid(team_id)


def get_available_teamid():
    return get_contest().get_available_teamid()
