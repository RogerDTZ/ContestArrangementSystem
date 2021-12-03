from util import *
import config
import contest
import seat


team_id2id = dict()


class Contestant:
    id: int
    team_id: int
    name: str
    sid: str
    affiliation: str
    seat_formatted_str: str
    password: str

    def __init__(self, contestant_id, team_id, name, sid, affiliation, seat_formatted_str=None, password=None):
        self.id = contestant_id
        self.team_id = team_id
        team_id2id[self.team_id] = self.id
        self.name = name
        self.sid = sid
        self.affiliation = affiliation
        self.seat_formatted_str = seat_formatted_str
        self.password = password

    def seated(self):
        return self.seat_formatted_str is not None

    def get_seat(self):
        return seat.decode_seat(self.seat_formatted_str)

    def serialize(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'name': self.name,
            'sid': self.sid,
            'affiliation': self.affiliation,
            'seat': self.seat_formatted_str,
            'password': self.password
        }

    def print(self, print_password=False, no_header=False):
        width = 100
        line = '+' + '-' * width + '+'
        if not no_header:
            print(line)
            print('|{}|'.format('Contestant Information'.center(width)))
            print(line)

        print(""" contestant id:  {}
 team_id:        {}
 name:           {}
 sid:            {}
 affiliation:    {}
 location:       {}
 password:       {}
{}""".format(
            self.id,
            self.team_id,
            self.name,
            self.sid if self.sid and len(self.sid) > 0 else '[None]',
            self.affiliation,
            self.seat_formatted_str if self.seat_formatted_str else '[Unseated]',
            self.password if print_password else ('[Generated]' if self.password else 'None'),
            line
        ))


g_init = False
g_contestants = dict()
g_contestant_unique = set()
g_contestant_max_id = 0


def create_contestant(contestant_id, team_id, name, sid, affiliation, seat_formatted_str=None, password=None):
    global g_init, g_contestants, g_contestant_unique, g_contestant_max_id

    if (name, sid, affiliation) in g_contestant_unique:
        error('Duplicate contestant: name={} sid={} affiliation={}'.format(name, sid, affiliation))
    # TODO: Verify that affiliation exists.
    if seat_formatted_str is not None:
        seat.occupy_seat(contestant_id, seat.decode_seat(seat_formatted_str))
    if not contest.occupy_teamid(team_id):
        error('Team id {} is not available (duplicate or out of range).'.format(team_id))

    g_contestants[contestant_id] = Contestant(contestant_id, team_id, name, sid, affiliation, seat_formatted_str, password)
    g_contestant_unique.add((name, sid, affiliation))
    g_contestant_max_id = max(g_contestant_max_id, contestant_id)


def get_contestants():
    global g_init, g_contestants, g_contestant_unique, g_contestant_max_id

    if g_init:
        return g_contestants
    g_init = True

    path = Path('.') / 'data' / 'contestants.json'
    data = list()
    if path.is_file():
        data = read_json(path)
    else:
        error('{} not found.'.format(path))

    for item in data:
        contestant_id = int(item['id'])
        team_id = int(item['team_id'])
        name = item['name']
        sid = item['sid'] if 'sid' in item and item['sid'] else ''
        affiliation = item['affiliation']
        seat_formatted_str = item['seat'] if 'seat' in item else None
        password = item['password'] if 'password' in item else None

        create_contestant(contestant_id, team_id, name, sid, affiliation, seat_formatted_str, password)

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
    global g_init, g_contestants, g_contestant_unique, g_contestant_max_id
    # Expect that global contest has been initialized.
    assert g_init
    g_contestant_max_id += 1
    return g_contestant_max_id


def show_information(contestant_id, show_password):
    contestants = get_contestants()
    if contestant_id not in contestants:
        error("Contestant {} not found.".format(contestant_id))
    contestants[contestant_id].print(show_password)


def show_information_all(show_password):
    contestants = get_contestants()
    if not ask_confirm('Are you sure to print {} contestants?'.format(len(contestants)), True):
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
    require_seat = ask_confirm('Seat the contestant?', True)
    gen_pass = ask_confirm('Generate a password?', True)
    contestant_id = get_available_id()
    team_id = contest.get_available_teamid()

    create_contestant(contestant_id, team_id, name, sid, affiliation)
    if require_seat:
        seat_contestant(contestant_id, manual=False, random_apply=False, override=False)
    if gen_pass:
        generate_password(contestant_id, config.args.pwd_alphabet, config.args.pwd_length)

    write_contestant_data()
    info('Successfully imported 1 contestant. (id = {})'.format(contestant_id))


def import_contestant(path: Path):
    if not path.is_file():
        error("File not found: {}".format(path))
    lines = read_tsv(path)
    if get_contestants_num() + len(lines) > contest.get_capacity():
        error("Importing contestants are beyond the capacity of contest.")

    for para in lines:
        if len(para) != 3:
            invalid_format('contestant csv', para.join('\t'))
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
    if contestant.seated():
        unseat_contestant(contestant_id, silent=True)
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


def seat_contestant(contestant_id, manual, random_apply, override, silent=False):
    contestants = get_contestants()

    if contestant_id not in contestants:
        error("Contestant {} not found.".format(contestant_id))
    c = contestants[contestant_id]

    if c.seated() and not override:
        error('Contestant {} is already seated at {}.'.format(contestant_id, c.get_seat().to_string()))

    if c.seated():
        unseat_contestant(contestant_id, silent=True)

    if manual:
        room = ask_variable('room')
        seat_id = ask_variable('seat id')
        s = seat.occupy_seat(contestant_id, seat.Seat(room, seat_id))
    else:
        s = seat.apply_seat(contestant_id, random_apply)

    contestants[contestant_id].seat_formatted_str = s.to_string()

    if not silent:
        info('Contestant {} is seated to [{}].'.format(contestant_id, s.to_string()))
    write_contestant_data()


def seat_all_contestants(random_apply, silent=False):
    contestants = get_contestants()
    cnt = 0
    for contestant_id, contestant in contestants.items():
        if not contestant.seated():
            cnt += 1
    if cnt == 0:
        normal('All contestants have already been seated.')
    if not ask_confirm('Are you sure to seat {} unseated contestant(s)?'.format(cnt), True):
        user_abort()

    for contestant_id, contestant in contestants.items():
        if not contestant.seated():
            seat_contestant(contestant_id, manual=False, random_apply=random_apply, override=False, silent=True)

    if not silent:
        info('Successfully seated {} contestant(s).'.format(cnt))


def unseat_contestant(contestant_id, silent=False):
    contestants = get_contestants()

    if contestant_id not in contestants:
        error("Contestant {} not found.".format(contestant_id))

    c = contestants[contestant_id]

    if not c.seated():
        error('Contestant {} does not have a seat yet.'.format(contestant_id))

    seat_str = c.seat_formatted_str

    seat.release_seat(seat.decode_seat(seat_str))
    c.seat_formatted_str = None

    if not silent:
        info('Contestant {} is unseated from [{}].'.format(contestant_id, seat_str))
    write_contestant_data()


def unseat_all_contestant(silent=False):
    contestants = get_contestants()

    cnt = 0
    for contestant_id, contestant in contestants.items():
        if contestant.seated():
            cnt += 1
    if cnt == 0:
        normal('All contestants have already been unseated.')
    if not ask_confirm('Are you sure to unseat {} seated contestant(s)?'.format(cnt), False):
        user_abort()

    for contestant_id, contestant in contestants.items():
        if contestant.seated():
            unseat_contestant(contestant_id, silent=True)

    if not silent:
        info('Successfully seated {} contestant(s).'.format(cnt))


def query_team_seat(team_id):
    if team_id not in team_id2id:
        error('Team {} does not exists.'.format(team_id))
    c = get_contestants()[team_id2id[team_id]]
    print('[{}]'.format(c.seat_formatted_str))
