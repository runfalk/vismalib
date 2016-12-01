from functools import wraps

__all__ = [
    "combomethod",
    "AttrProxy",
]

class combomethod(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.func(obj_type, obj, *args, **kwargs)
        return wrapper


class AttrProxy(object):
    """
    Attribute proxy descriptor.

    Allows accessing and setting attributes in an object hierarchy.

    :param attr: Attribute name (string) to proxy. If the attribute is on a
                 child object attributes are separated by a ".".
    """

    __slots__ = ("path")

    def __init__(self, attr):
        self.path = attr.split(".")

    def _get_target(self, obj):
        target = obj
        for attr in self.path[:-1]:
            target = getattr(target, attr)
        return target

    def __get__(self, obj, obj_type):
        return getattr(self._get_target(obj), self.path[-1])

    def __set__(self, obj, value):
        setattr(self._get_target(obj), self.path[-1], value)
