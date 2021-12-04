import argparse
import string

args = argparse.Namespace()


default_args = {
    'pwd_alphabet': string.ascii_uppercase + string.digits,
    'pwd_length': 8,
    'manual_seat': False,
    'override_seat': False,
    'random_apply_seat': False,
}


def set_default_args():
    for arg, value in default_args.items():
        if not hasattr(args, arg):
            setattr(args, arg, value)
