# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


#
# python extract_multipart_data_from_har.py harfilename.har
#

from typing import Generator
from urllib.parse import unquote
import base64
import json
import mimetypes
import os
import re
import sys


# ----------------------------------------------------------------------------
# Setup non-standard mime-types
# ----------------------------------------------------------------------------

# these mimetypes are non-standard, but used at various places

# usually its image/jpeg, see mimetypes.types_map for all known types
mimetypes.add_type("image/jpg", ".jpg")

# ----------------------------------------------------------------------------
# Generic functions
# ----------------------------------------------------------------------------


def replace_non_alphanumeric(text):
    """Replaces non-alphanumeric characters with underscores in the given text."""

    # Compile the pattern once for efficiency
    pattern = re.compile(r'[^a-zA-Z0-9]')
    return pattern.sub('_', text)


def split_bytes_by_boundary(data: bytes, boundary: bytes) -> list[bytes]:
    """
    Splits bytes-like data into parts based on a boundary delimiter.

    Args:
        data: The bytes to split.
        boundary: The boundary delimiter (also bytes).

    Returns:
        A list of bytes, each representing a part of the original data.
    """

    parts = []
    start = 0
    while True:
        end = data.find(boundary, start)
        if end == -1:
            parts.append(data[start:])
            break
        parts.append(data[start:end])
        start = end + len(boundary)

    return parts


# ----------------------------------------------------------------------------
# multipart functions 
# ----------------------------------------------------------------------------

def decode_content(content: bytes, base64_encoded=False) -> bytes:
    try:
        if base64_encoded:
            return base64.b64decode(content)
        else:
            return content
    except base64.binascii.Error:
        print(f"Error: Invalid base64 encoding")
        return content


def parse_part(part: bytes) -> tuple[dict, bytes] | None:
    end = part.find(b"\r\n\r\n", 0)
    if end > -1:
        header_part = part[:end]
        data_part = part[end:]
        header = {}
        for header_field in split_bytes_by_boundary(header_part, b"\r\n"):
            header_parts = header_field.decode("utf-8").split(":")
            if len(header_parts) == 2:
                key = header_parts[0].strip().lower()
                value = unquote(header_parts[1].strip())
                if key == "content-length":
                    header[key] = int(value)
                else:
                    header[key] = value
        raw_data_length = header.get("content-length", len(data_part) - 6)
        raw_data = data_part[4:4+raw_data_length]
        return (header, raw_data)

    return None


def parse_content_disposition(content_disposition: str) -> Generator[tuple[str, str], None, None]:
    """
    Example:
        inline; name=P/filename.png;\nfilename=filename
    """
    parts = content_disposition.split(";", maxsplit=-1)
    for part in parts:
        subparts = part.split("=")
        if len(subparts) == 2:
            key = subparts[0].strip()
            value = subparts[1].strip()
            yield (key, value)


def extract_multipart_data(decoded_data: bytes, boundary: bytes) -> bool:
    count = 0
    for part in split_bytes_by_boundary(decoded_data, boundary):
        result = parse_part(part)
        if result:
            (header, raw_data) = result
            extension = mimetypes.guess_extension(header.get("content-type", ""))
            if not extension:
                extension = ".unknown"
            count += 1
            filename = f"file-{count}{extension}"
            for (key, value) in parse_content_disposition(header.get("content-disposition", "")):
                if key == "name":
                    filename = replace_non_alphanumeric(value) + extension
                    break
            if not os.path.exists(filename):
                open(filename, "wb").write(raw_data)
                print(f"Writing filename = {filename}")
            else:
                print(f"Skip writing, filename = {filename} exists.")
    return True


def process_multipart_data(data: bytes, boundary: str, extract=False, base64_encoded=False) -> bool:
    """Processes a data (optionally encoded in base64)."""
    decoded_data = decode_content(data, base64_encoded)

    if extract and decoded_data:
        boundary_bytes = f"--{boundary}".encode("utf-8")
        return extract_multipart_data(decoded_data, boundary_bytes)
    else:
        return False


# ----------------------------------------------------------------------------
# Process functions
# ----------------------------------------------------------------------------

def filter_entries(entries_obj, filter_func=None):
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
    for item in entries_obj:
        for key, value in item.items():
            if filter_func:
                if filter_func(key, value):
                    yield (key, value)
            else:
                yield (key, value)


def process_har_file(filename):
    # default file format for .har is set to utf-8, to support them
    jsonobject = json.loads(open(filename, "r", encoding="utf-8").read())
    log_obj = jsonobject.get("log", {})
    entries_obj = log_obj.get("entries", {})
    extract_filtered_multipart_data(entries_obj)


# ----------------------------------------------------------------------------
# Extract functions
# ----------------------------------------------------------------------------


def extract_filtered_multipart_data(entries_obj):
    filter_fun = lambda key, value: key == "response" and filter_for_multipart_mixed_response(value)
    for (key, value) in filter_entries(entries_obj, filter_fun):
        content_type = ""
        for header in value.get("headers", []):
            if header["name"] == "content-type":
                content_type = header["value"]
                break
        boundary = content_type.split(";")[-1].strip().split("=")[-1].strip()
        content = value.get("content", {})
        content_text = content.get("text", "")
        content_encoding = content.get("encoding", "")
        is_base64_encoding = (content_encoding == "base64")
        process_multipart_data(content_text.encode("utf-8"), boundary, extract=True, base64_encoded=is_base64_encoding)



# ----------------------------------------------------------------------------
# Filter functions
# ----------------------------------------------------------------------------


def filter_for_multipart_mixed_response(value):
    for header in value.get("headers", []):
        if header["name"] == "content-type":
            return header["value"].startswith("multipart/mixed;")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main():
    har_filename = sys.argv[1]
    process_har_file(har_filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())