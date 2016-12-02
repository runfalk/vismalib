from functools import wraps

__all__ = [
    "combomethod",
    "getattrdeep",
    "AttrProxy",
]


class UnsetType(object):
    """
    Unset sentinel for detrmining whether an argument was passed or not.
    """
    __slots__ = ()
Unset = UnsetType()


class combomethod(object):
    """
    Allows a method to work both as a class method and an instance method.

        class SomeClass(object):
            @combomethod
            def multimethod(cls, self):
                if self is None:
                    print("I am a class method")
                else:
                    print("I am an instance method")

    If the method is called as a class method, ``self`` is ``None``, otherwise
    it will be the current object. ``cls`` is always defined.

    :param func: Method to decorate
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.func(obj_type, obj, *args, **kwargs)
        return wrapper


def getattrdeep(object, attrs, default=Unset):
    """
    An implementation of ``getattr`` that works in multiple levels in an
    object hierarchy. ``getattrdeep(x, ["y", "z"])``is equivalent to
    ``x.y.z``.

    :param object: Object to start lookup from.
    :param attrs: Array of attribute names in string format.
    :param default: Default value if an attribute is not found.
    :raise AttributeError: if ``default`` is not provided and one of the
                           given attribute names results in an AttributeError.
    """

    target = object
    for attr in attrs:
        if default is Unset:
            target = getattr(target, attr)
        else:
            target = getattr(target, attr, default)
    return target


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
        return getattrdeep(obj, self.path[:-1])

    def __get__(self, obj, obj_type):
        return getattr(self._get_target(obj), self.path[-1])

    def __set__(self, obj, value):
        setattr(self._get_target(obj), self.path[-1], value)
