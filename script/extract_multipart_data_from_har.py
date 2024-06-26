# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


#
# python extract_multipart_data_from_har.py harfilename.har
#

from multipart_util import (
    process_multipart_data,
)

from typing import Generator
from urllib.parse import unquote

import json
import os
import re
import sys


# ----------------------------------------------------------------------------
# Process functions
# ----------------------------------------------------------------------------

def filter_entries(entries_obj: dict, filter_func=None) -> Generator[tuple[int, str, str], None, None]:
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
                    yield (index, key, value)
            else:
                yield (index, key, value)


def process_har_file(filename: str) -> None:
    # default file format for .har is set to utf-8, to support them
    jsonobject = json.loads(open(filename, "r", encoding="utf-8").read())
    log_obj = jsonobject.get("log", {})
    entries_obj = log_obj.get("entries", {})
    extract_filtered_multipart_data(entries_obj)


# ----------------------------------------------------------------------------
# Extract functions
# ----------------------------------------------------------------------------


def extract_filtered_multipart_data(entries_obj: dict) -> None:
    filter_fun = lambda key, value: key == "response" and filter_for_multipart_mixed_response(value)
    for (index, key, value) in filter_entries(entries_obj, filter_fun):
        content_type = ""
        for header in value.get("headers", []):
            if header.get("name", "").strip().lower() == "content-type":
                content_type = header.get("value", "")
                break
        boundary = content_type.split(";")[-1].strip().split("=")[-1].strip()
        content = value.get("content", {})
        content_text = content.get("text", "")
        content_encoding = content.get("encoding", "")
        is_base64_encoding = (content_encoding == "base64")
        process_multipart_data(content_text.encode("utf-8"), boundary, index, extract=True, base64_encoded=is_base64_encoding)



# ----------------------------------------------------------------------------
# Filter functions
# ----------------------------------------------------------------------------


def filter_for_multipart_mixed_response(value: dict) -> str:
    for header in value.get("headers", []):
        if header.get("name", "").strip().lower() == "content-type":
            return header.get("value", "").startswith("multipart/mixed;")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    har_filename = sys.argv[1]
    process_har_file(har_filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())