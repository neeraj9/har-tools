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

from har_common import filter_entries

import json
import os
import sys
from typing import Generator


# ----------------------------------------------------------------------------
# Process functions
# ----------------------------------------------------------------------------


def process_har_file(filename: str) -> None:
    # default file format for .har is set to utf-8, to support them
    jsonobject = json.loads(open(filename, "r", encoding="utf-8").read())
    log_obj = jsonobject.get("log", {})
    entries_obj = log_obj.get("entries", {})
    for (output_filename, raw_data, content_type) in extract_filtered_multipart_data(entries_obj):
        if not os.path.exists(output_filename):
            open(output_filename, "wb").write(raw_data)
            print(f"Writing filename = {output_filename}")
        else:
            print(f"Skip writing, filename = {output_filename} exists.")


# ----------------------------------------------------------------------------
# Extract functions
# ----------------------------------------------------------------------------


def extract_filtered_multipart_data(entries_obj: dict) -> Generator[tuple[str, bytes, str], None, None]:
    filter_fun = lambda key, value: key == "response" and filter_for_multipart_mixed_response(value)

    for (index, key, value, item) in filter_entries(entries_obj, filter_fun):
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

        for (output_filename, raw_data, content_type) in process_multipart_data(
            content_text.encode("utf-8"), boundary, index, extract=True, base64_encoded=is_base64_encoding):

            yield (output_filename, raw_data, content_type)


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