#!/usr/bin/env python3
"""
Do you know where can I learn Python?
"""
import pymongo


def schools_by_topic(mongo_collection, topic):
    """
    find by specific value
    """
    return mongo_collection.find({"topics":  {"$in": [topic]}})
