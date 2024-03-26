import base64
import os
import types


def is_primitive(val):
    primitive = (int, str, bool, float, bytes, types.NoneType)
    return isinstance(val, primitive)


def get_short_id(length=10):
    return base64.b64encode(os.urandom(32))[:length].decode('utf-8')
