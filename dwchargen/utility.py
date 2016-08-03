import random

#-------------------------------------------------------------------------------
class RegistryClass(type):
    def __new__(mcls, name, bases, dict):
        cls = type.__new__(mcls, name, bases, dict)
        if not getattr(cls, 'registry_ignore', False):
            if hasattr(cls, 'classes') and AbstractSubRegistry not in bases:
                cls.classes.append(cls)
            if any(bcls is not object and bcls is Registry for bcls in bases):
                cls.classes = []
        return cls

class AbstractSubRegistry(object):
    __metaclass__ = RegistryClass
class Registry(object):
    __metaclass__ = RegistryClass

class Random(object):
    frequency = 1

    @classmethod
    def random_class(cls):
        if isinstance(cls, RegistryClass) and cls not in cls.classes:
            sum_freq = 0
            for subcls in cls.classes:
                sum_freq += subcls.frequency
            choice = random.uniform(0, sum_freq)
            for subcls in cls.classes:
                if subcls.frequency > choice: break
                choice -= subcls.frequency
            return subcls
        else:
            return cls

    @classmethod
    def new_random(cls, *args, **kwds):
        cls = cls.random_class()
        obj = cls()
        obj.set_random(*args, **kwds)
        return obj

    def set_random(self, *args):
        pass

    def apply_random(self, *args):
        pass

class Wrapper(object):
    def __init__(self, target, **kwds):
        self.__dict__.update(kwds)
        self.__target = target
    def __getattr__(self, name):
        return getattr(self.__target, name)
