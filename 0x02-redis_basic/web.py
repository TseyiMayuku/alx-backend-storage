#!/usr/bin/env python3
"""
A cache task file
"""
import requests
import redis


store = redis.Redis()


def get_page(url: str) -> str:
    """get html elements of a url"""
    key_for_cache = "cached:" + url
    data_from_cache = store.get(key_for_cache)
    if data_from_cache:
        return data_from_cache.decode("utf-8")

    result = requests.get(url)
    html = result.text

    ke_counter = "count:" + url
    store.incr(ke_counter)
    store.set(key_for_cache, html)
    store.expire(key_for_cache, 10)
    return html
