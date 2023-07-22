#!/usr/bin/env python3
"""This module declares a redis class and methods"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def call_counters(method: Callable) -> Callable:
    '''count calling of methods of the cache class'''
    id = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''return wrapped decor function'''
        self._redis.incr(id)
        return method(self, *args, **kwargs)
    return wrapper


def call_log(method: Callable) -> Callable:
    '''history store function for input and output'''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''return wrapped decor function'''
        func_input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", func_input)
        out = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", out)
        return out
    return wrapper


def replay(fn: Callable):
    '''display the history of calls of a particular function.'''
    red = redis.Redis()
    fucntion_name = fn.__qualname__
    call_ = red.get(fucntion_name)
    try:
        call_ = int(c.decode("utf-8"))
    except Exception:
        call_ = 0
    print("{} was called {} times:".format(fucntion_name, c))
    ins = red.lrange("{}:inputs".format(fucntion_name), 0, -1)
    outs = red.lrange("{}:outputs".format(fucntion_name), 0, -1)
    for input, output in zip(ins, outs):
        try:
            input = input.decode("utf-8")
        except Exception:
            input = ""
        try:
            output = output.decode("utf-8")
        except Exception:
            output = ""
        print("{}(*{}) -> {}".format(fucntion_name, input, output))



class Cache:
    '''A cache class for Reddis'''
    def __init__(self):
        '''Save an instance on initialization'''
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_log
    @call_counters
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''take data to store - return string'''
        reddisKey = str(uuid4())
        self._redis.set(reddisKey, data)
        return reddisKey

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''change data format'''
        storedValue = self._redis.get(key)
        if fn:
            storedValue = fn(storedValue)
        return storedValue


    def get_str(self, key: str) -> str:
        '''get string with key'''
        stored_value = self._redis.get(key)
        return stored_value.decode("utf-8")


    def get_int(self, key: str) -> int:
        '''get string with key from cache'''
        val = self._redis.get(key)
        try:
            val = int(val.decode("utf-8"))
        except Exception:
            val = 0
        return val
