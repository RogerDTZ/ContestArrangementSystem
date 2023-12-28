from util import *
import config
import contestant


g_init = False
# Map from seat to contestant.
g_seat_map = dict()
# Available seats.
g_available = set()


class Seat:
    room: str
    seat_id: str

    def __init__(self, room, seat_id):
        self.room = room
        self.seat_id = seat_id

    def to_string(self):
        return '{}-{}'.format(self.room, self.seat_id)


def write_seats_data():
    path = Path('.') / 'data' / 'seats.tsv'
    data = []
    for seat_pair in g_seat_map:
        data.append([seat_pair[0], seat_pair[1]])
    write_tsv(path, data)


def valid_formatted_seat(formatted_str: str):
    if formatted_str != formatted_str.strip():
        return False
    if formatted_str.count('-') != 1:
        return False
    return True


def decode_seat(formatted_str):
    if not valid_formatted_seat(formatted_str):
        invalid_format('Seat', formatted_str)
    seat_info = formatted_str.strip().split('-')
    return Seat(seat_info[0], seat_info[1])


def create_seat(room, seat_id):
    seat = (room, seat_id)
    if seat in g_seat_map:
        error('Duplicate seat: [{}].'.format(Seat(room, seat_id).to_string()))
    g_seat_map[seat] = -1
    g_available.add(seat)
    return Seat(room, seat_id)


def remove_seat(room, seat_id, silent=False):
    seat = (room, seat_id)
    if seat not in g_seat_map:
        error('Seat [{}] does not exists.'.format(Seat(room, seat_id).to_string()))
    if g_seat_map[seat] != -1:
        error('Seat [{}] is still occupied by contestant {}.'.format(Seat(room, seat_id).to_string(), g_seat_map[seat]))
    g_seat_map.pop(seat)
    if seat in g_available:
        g_available.remove(seat)

    write_seats_data()
    if not silent:
        info('Successfully deleted seat [{}].'.format(Seat(room, seat_id).to_string()))


def get_seats():
    global g_init, g_seat_map, g_available

    if g_init:
        return g_seat_map, g_available
    g_init = True

    path = Path('.') / 'data' / 'seats.tsv'
    import_seats(path, silent=True, write=False)

    return g_seat_map, g_available


def create_seat_interactive():
    s = create_seat(config.args.room, config.args.seat_id)

    write_seats_data()
    info('Created seat [{}].'.format(s.to_string()))


def import_seats(path: Path, silent=False, write=True):
    if not path.is_file():
        error("File not found: {}".format(path))
    data = read_tsv(path)

    for item in data:
        if len(item) != 2:
            invalid_format(path, item)
        room = item[0]
        seat_id = item[1]
        create_seat(room, seat_id)

    if not silent:
        info('Successfully imported {} seats.'.format(len(data)))

    if write:
        write_seats_data()


def apply_seat(contestant_id, random_choose, room_mask):
    seat_map, available = get_seats()
    use_mask = room_mask is not None and len(room_mask) > 0
    if use_mask:
        filtered_avai_seats = set([seat for seat in available if seat[0] in room_mask])
    if (not use_mask and len(available) == 0) or (use_mask and len(filtered_avai_seats) == 0):
        error('No available seats.')
    if random_choose:
        if not use_mask:
            seat = available.pop()
        else:
            seat = filtered_avai_seats.pop()
            available.remove(seat)
    else:
        if not use_mask:
            seat = min(available)
            available.remove(seat)
        else:
            seat = min(filtered_avai_seats)
            filtered_avai_seats.remove(seat)
            available.remove(seat)
    seat_map[seat] = contestant_id
    return Seat(seat[0], seat[1])


def occupy_seat(contestant_id, seat: Seat):
    seat_map, available = get_seats()
    seat_formatted_string = seat.to_string()
    seat = (seat.room, seat.seat_id)

    if seat not in seat_map:
        error('Cannot seat contestant {}: Seat [{}] does not exists.'.format(contestant_id, seat_formatted_string))
    if seat_map[seat] != -1:
        error('Cannot seat contestant {}: Seat [{}] is already occupied by contestant {}.'.format(contestant_id, seat_formatted_string, seat_map[seat]))

    seat_map[seat] = contestant_id
    available.remove(seat)
    return Seat(seat[0], seat[1])


def release_seat(seat: Seat):
    seat_map, available = get_seats()
    seat_formatted_string = seat.to_string()
    seat = (seat.room, seat.seat_id)

    if seat not in seat_map:
        error('Seat [{}] does not exists.'.format(seat_formatted_string))
    if seat_map[seat] == -1:
        error('Seat [{}] is already free.'.format(seat_formatted_string))

    seat_map[seat] = -1
    available.add(seat)


def show_seat(seat: Seat):
    seat_map, available = get_seats()
    seat_formatted_string = seat.to_string()
    seat = (seat.room, seat.seat_id)

    if seat not in seat_map:
        error('Seat [{}] does not exists.'.format(seat_formatted_string))
    if seat_map[seat] == -1:
        print('Seat [{}] is free.'.format(seat_formatted_string))
    else:
        contestant_id = seat_map[seat]
        print('Seat [{}] is occupied by contestant {}:'.format(seat_formatted_string, contestant_id))
        contestant.get_contestants()[contestant_id].print()


def show_room(room: str):
    seats = get_seats()[0]
    res = list()
    for s in seats:
        if s[0] != room:
            continue
        res.append((Seat(s[0], s[1]).to_string(), '[]' if seats[s] == -1 else '[{}]'.format(seats[s])))
    if len(res) == 0:
        error('Room {} not found.'.format(room))
    width = 30
    print(table_line(width))
    print(table_row('Room {}'.format(room), width))
    print(table_line(width))
    for i in range(len(res)):
        s = res[i]
        print(table_row(format('{}: {}'.format(s[0], s[1])), 30, 8))
    print(table_line(width))


def get_room_num():
    seats = get_seats()[0]
    room = set()
    for s in seats:
        room.add(s[0])
    return len(room)


def get_room_info():
    seats = get_seats()[0]
    d = dict()
    for s in seats:
        if s[0] not in d:
            d[s[0]] = (0, 0)
        d[s[0]] = (d[s[0]][0] + 1, d[s[0]][1])
        if seats[s] != -1:
            d[s[0]] = (d[s[0]][0], d[s[0]][1] + 1)
    res = str()
    tot = len(d)
    cur = 0
    for room, (total_seat_num, occupied_num) in d.items():
        res += '{}[{}/{}]'.format(room, occupied_num, total_seat_num)
        cur += 1
        if cur != tot:
            res += ', '
    if len(res) == 0:
        res = 'No room'
    return res


def get_seats_num():
    return len(get_seats()[0])
