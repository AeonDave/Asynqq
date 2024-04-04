import random
import string
import types


def is_primitive(val):
    primitive = (int, str, bool, float, bytes, types.NoneType)
    return isinstance(val, primitive)


def get_short_id(prefix='', length=10) -> str:
    chars = string.ascii_letters + string.digits
    return prefix + ''.join(random.choices(chars, k=length))
