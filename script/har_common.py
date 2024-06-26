# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from typing import Generator


def filter_entries(entries_obj: dict, filter_func=None) -> Generator[tuple[int, str, str, dict], None, None]:
    """
    Keys:
        _initiator
        _priority
        _resourceType
        cache
        pageref
        request
        response
        serverIPAddress
        startedDateTime
        time
        timings
    """
    index = 0
    for item in entries_obj:
        index += 1
        for key, value in item.items():
            if filter_func:
                if filter_func(key, value):
                    yield (index, key, value, item)
            else:
                yield (index, key, value, item)