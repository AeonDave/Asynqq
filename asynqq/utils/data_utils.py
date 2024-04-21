import random
import string
import types


def is_primitive(val) -> bool:
    """
    Check if a value is a primitive type.

    Parameters:
    :param val: The value to check.

    Returns:
    :return bool: True if the value is a primitive type, False otherwise.
    """
    primitive = (int, str, bool, float, bytes, types.NoneType)
    return isinstance(val, primitive)


def get_short_id(prefix: str = '', length: int = 10) -> str:
    """
    Generate a short identifier string.

    Parameters:
    :param  prefix: The prefix to add to the generated identifier. Defaults to ''.
    :param  length: The length of the identifier to generate. Defaults to 10.

    Returns:
    :return str: The generated identifier.
    """
    chars = string.ascii_letters + string.digits
    return prefix + ''.join(random.choices(chars, k=length))
