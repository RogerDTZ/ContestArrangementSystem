import string

from util import *
import config
import contest


class Contestant:
    id: int
    team_id: int
    name: str
    sid: str
    affiliation: str
    seat: str
    password: str

    def __init__(self, contestant_id, team_id, name, sid, affiliation, seat=None, password=None):
        self.id = contestant_id
        self.team_id = team_id
        self.name = name
        self.sid = sid
        self.affiliation = affiliation
        self.seat = seat
        self.password = password

    def serialize(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'name': self.name,
            'sid': self.sid,
            'affiliation': self.affiliation,
            'seat': self.seat,
            'password': self.password
        }

    def print(self, print_password=False, no_header=False):
        if not no_header:
            print("""
+------------------------------+
|    Contestant Information    |
+------------------------------+""")

        print(""" contestant id:  {}
 team_id:        {}
 name:           {}
 sid:            {}
 affiliation:    {}
 location:       {}
 password:       {}
+------------------------------+""".format(
            self.id,
            self.team_id,
            self.name,
            self.sid if self.sid and len(self.sid) > 0 else '[None]',
            self.affiliation,
            self.seat if self.seat else '[Unseated]',
            self.password if print_password else ('[Generated]' if self.password else 'None')))


g_contestants = None
g_contestant_unique = None
g_contestant_max_id = 0


def create_contestant(contestant_id, team_id, name, sid, affiliation, seat=None, password=None):
    global g_contestants, g_contestant_unique, g_contestant_max_id

    if g_contestants is None:
        g_contestants = dict()
        g_contestant_unique = set()
        g_contestant_max_id = 0

    if (name, sid, affiliation) in g_contestant_unique:
        error('Duplicate contestant: name={} sid={} affiliation={}'.format(name, sid, affiliation))
    # TODO: Verify that affiliation exists.
    # TODO: Verify that seat exists.
    if not contest.occupy_teamid(team_id):
        error('Team id {} is not available (duplicate or out of range).'.format(team_id))

    g_contestants[contestant_id] = (Contestant(contestant_id, team_id, name, sid, affiliation, seat, password))
    g_contestant_unique.add((name, sid, affiliation))
    g_contestant_max_id = max(g_contestant_max_id, contestant_id)


def get_contestants():
    global g_contestants, g_contestant_unique, g_contestant_max_id
    if g_contestants is not None:
        return g_contestants

    path = Path('.') / 'data' / 'contestants.json'
    if path.is_file():
        data = read_json(path)
    else:
        data = []

    g_contestants = dict()
    g_contestant_unique = set()
    g_contestant_max_id = 0

    for item in data:
        contestant_id = int(item['id'])
        team_id = int(item['team_id'])
        name = item['name']
        sid = item['sid'] if 'sid' in item and item['sid'] else ''
        affiliation = item['affiliation']
        seat = item['seat'] if 'seat' in item else None
        password = item['password'] if 'password' in item else None

        create_contestant(contestant_id, team_id, name, sid, affiliation, seat, password)

    return g_contestants


def write_contestant_data():
    contestants = get_contestants()
    path = Path('.') / 'data' / 'contestants.json'
    data = list()
    for contestant_id in contestants:
        contestant = contestants[contestant_id]
        data.append(contestant.serialize())
    write_json(path, data)


def get_available_id():
    global g_contestants, g_contestant_unique, g_contestant_max_id
    if g_contestants is None:
        get_contestants()
    g_contestant_max_id += 1
    return g_contestant_max_id


def show_information(contestant_id, show_password):
    contestants = get_contestants()
    if contestant_id not in contestants:
        error("Contestant {} not found.".format(contestant_id))
    contestants[contestant_id].print(show_password)


def show_information_all(show_password):
    contestants = get_contestants()
    if not ask_confirm('Are you sure to print {} contestants?'.format(len(contestants)), False):
        user_abort()
    first = True
    for contestant_id, contestant in contestants.items():
        contestant.print(print_password=show_password, no_header=False if first else True)
        first = False


def get_contestants_num():
    return len(get_contestants())


def create_contestant_interactive():
    if contest.contest_full():
        error('The contest is full. Check available team ids and available seats.')
    name = ask_variable('name')
    sid = ask_variable('SID', '')
    affiliation = ask_variable('affiliation')
    map_seat = ask_confirm('Map a seat?', True)
    gen_pass = ask_confirm('Generate a password?', True)
    contestant_id = get_available_id()
    team_id = contest.get_available_teamid()

    create_contestant(contestant_id, team_id, name, sid, affiliation)
    # TODO: seat the contestant if needed.
    if gen_pass:
        generate_password(contestant_id, config.args.pwd_alphabet, config.args.pwd_length)

    write_contestant_data()
    info('Successfully imported 1 contestant. (id = {})'.format(contestant_id))


def import_contestant(path: Path):
    if not path.is_file():
        error("File not found: {}".format(path))
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if get_contestants_num() + len(lines) > contest.get_capacity():
        error("Importing contestants are beyond the capacity of contest.")

    for line in lines:
        para = line.strip().split('\t')
        if len(para) != 3:
            invalid_format('contestant csv', line)
        name = para[0]
        sid = para[1]
        affiliation = para[2]
        contestant_id = get_available_id()
        team_id = contest.get_available_teamid()
        create_contestant(contestant_id, team_id, name, sid, affiliation)

    write_contestant_data()
    info('Successfully imported {} contestants.'.format(len(lines)))


def remove_contestant(contestant_id):
    contestants = get_contestants()
    if contestant_id not in contestants:
        error('Contestant {} not found.'.format(contestant_id))
    contestant = contestants[contestant_id]

    global g_contestants, g_contestant_unique
    contest.release_teamid(contestant.team_id)
    # TODO: release the seat if seated.
    g_contestant_unique.remove((contestant.name, contestant.sid, contestant.affiliation))
    g_contestants.pop(contestant_id)

    write_contestant_data()
    info('Successfully remove contestant {}.'.format(contestant_id))


def generate_password(contestant_id, alphabet, length, override=False):
    contestant = get_contestants()[contestant_id]
    if contestant.password and not override:
        error('Contestant {} has already have a password.'.format(contestant_id))
    contestant.password = generate_random_password(alphabet, length)

    write_contestant_data()
    info('Successfully generate password for contestant {}.'.format(contestant_id))


def generate_password_for_all(alphabet, length, override=False):
    contestants = get_contestants()
    if not ask_confirm('Are you sure to generate password for {} contestant(s)?'.format(len(contestants)), False):
        user_abort()

    for contestant_id in contestants:
        contestant = contestants[contestant_id]
        if contestant.password and not override:
            error('Contestant {} has already have a password.'.format(contestant_id))
        contestant.password = generate_random_password(alphabet, length)

    write_contestant_data()
    info('Successfully generate password for {} contestant(s).'.format(len(contestants)))

