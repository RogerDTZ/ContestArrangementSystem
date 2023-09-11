from util import *
import config
import contestant


g_init = False
g_affiliations = dict()


def write_affiliations_data():
    path = Path('.') / 'data' / 'affiliations.tsv'
    data = []
    for shortname, fullname in g_affiliations.items():
        data.append([shortname, fullname])
    write_tsv(path, data)


def create_affiliation(shortname, fullname):
    if shortname in g_affiliations:
        error('Duplicate affiliation: {}.'.format(shortname))
    g_affiliations[shortname] = fullname


def get_affiliations():
    global g_init, g_affiliations

    if g_init:
        return g_affiliations
    g_init = True

    path = Path('.') / 'data' / 'affiliations.tsv'
    import_affiliations(path, silent=True, write=False)

    return g_affiliations


def create_affiliation_interactive():
    shortname = ask_variable('shortname')
    fullname = ask_variable('full name')
    create_affiliation(shortname, fullname)

    write_affiliations_data()
    info('Successfully added affiliation [{}] {}.'.format(shortname, fullname))


def import_affiliations(path: Path, silent=False, write=True):
    if not path.is_file():
        error('File not found: {}'.format(path))
    data = read_tsv(path)

    for item in data:
        if len(item) != 2:
            invalid_format(path, item)
        shortname = item[0]
        fullname = item[1]
        create_affiliation(shortname, fullname)

    if not silent:
        info('Successfully imported {} affiliations.'.format(len(data)))

    if write:
        write_affiliations_data()


def remove_affiliation(shortname):
    affiliations = get_affiliations()
    if shortname not in affiliations:
        error('Affiliation {} not found.'.format(shortname))

    for _, c in contestant.get_contestants().items():
        if c.aff == shortname:
            error('Affiliation {} still has members such as contestant {}.'.format(shortname, c.id))

    fullname = affiliations[shortname]
    affiliations.pop(shortname)

    write_affiliations_data()
    info('Successfully deleted affiliation [{}] {}.'.format(shortname, fullname))


def show_affiliation(shortname, cnt=-1, no_header=False):
    affiliations = get_affiliations()
    if shortname not in affiliations:
        error('Affiliation {} not found.'.format(shortname))
    width = 60
    left = 10
    if cnt == -1:
        cnt = len([x for _, x in contestant.get_contestants().items() if x.aff == shortname])
    if not no_header:
        print(table_line(width))
        print(table_row('Affiliation Information', width))
        print(table_line(width))
    print(table_row('name:             {}'.format(affiliations[shortname]), width, left))
    print(table_row('shortname:        {}'.format(shortname), width, left))
    print(table_row('contestants:      {}'.format(cnt), width, left))
    print(table_line(width))


def show_all_affiliations():
    if not ask_confirm('Are you sure to print {} affiliations?'.format(get_affiliations_num()), True):
        user_abort()
    count = dict()
    for shortname in get_affiliations():
        count[shortname] = 0
    for _, c in contestant.get_contestants().items():
        aff = c.aff
        if aff is None:
            continue
        count[aff] += 1

    first = True
    for shortname, num in count.items():
        show_affiliation(shortname, num, not first)
        first = False


def get_affiliations_num():
    return len(get_affiliations())
