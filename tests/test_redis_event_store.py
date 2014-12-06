# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import time

logging.basicConfig(level=logging.DEBUG)

import pytest

from meepo.apps.event_store import MRedisEventStore


@pytest.fixture(scope="function")
def redis_event_store(request, redis_dsn):
    event_store = MRedisEventStore(redis_dsn)

    def fin():
        event_store.r.flushdb()

    request.addfinalizer(fin)
    return event_store


def test_redis_event_store_add(redis_event_store):
    # add event
    for pk in (1, 3):
        redis_event_store.add("test_write", pk)
        time.sleep(1)

    # test event store add
    assert redis_event_store.get_all("test_write") == ['1', '3']

    # re-add pk will refresh the score to newer timestamp
    redis_event_store.add("test_write", 1)
    assert redis_event_store.get_all("test_write") == ['3', '1']


def test_redis_event_store_add_by_ts(redis_event_store):
    start_time = int(time.time())
    times = list(range(start_time, start_time + 5))

    # add event
    for i, pk in enumerate(range(1, 10, 2)):
        redis_event_store.add("test_write", pk, ts=times[i])

    # test event store with timestamp passed
    stores = redis_event_store.get_all("test_write", with_ts=True)
    assert [s[0] for s in stores] == ['1', '3', '5', '7', '9']
    assert times == [s[1] for s in stores]
