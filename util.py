import sys
import re
import yaml
from pathlib import Path


def user_abort(msg):
    if msg:
        print('User abort: {}'.format(msg))
    else:
        print('User abort.')
    exit(0)


def invalid_format(arg_name, arg_value):
    print('Invalid format: {} is in wrong format: {}'.format(arg_name, arg_value))
    exit(1)


def invalid_arg(arg_name, arg_value):
    print('Invalid argument: {} is invalid: {}'.format(arg_name, arg_value))
    exit(1)


def error(msg):
    print('ERROR: {}'.format(msg))
    exit(1)


def fatal(msg):
    print('FATAL: {}'.format(msg))
    exit(1)


def ask_variable(name, default=None):
    if default is None:
        val = ''
        while True:
            print(f"{name}: ", end='', file=sys.stderr)
            val = input()
            if val == '':
                print(f"{name} must not be empty!", file=sys.stderr)
            else:
                break
        return val
    else:
        print(f"{name} [{default}]: ", end='', file=sys.stderr)
        val = input()
        return default if val == '' else val


def read_yaml(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def write_yaml(path: Path, data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data=data, stream=f, allow_unicode=True)


def decode_range(data: str, range_name='range'):
    data = data.strip()
    if not re.match('[0-9]*-[0-9]*$', data):
        invalid_format(range_name, data)
    res = tuple(list(map(int, data.split('-'))))
    if res[0] > res[1]:
        invalid_arg(range_name, res)
    return res


def encode_range(low: int, high: int):
    return '{}-{}'.format(low, high)

