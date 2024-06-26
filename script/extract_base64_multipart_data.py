# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


#
# python extract_base64_multipart_data.py "2f9825ee3f2949949f1210caa1978960" multipart.txt
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


def replace_non_alphanumeric(text: str) -> str:
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

def process_base64_multipart_data_file(filename: str, boundary: str):
    data = open(filename, "rb").read()
    if data.startswith(b"data:multipart/mixed;base64,"):
            data = data[len(b"data:multipart/mixed;base64,"):]
    return process_multipart_data(data, boundary, extract=True, base64_encoded=True)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    boundary = sys.argv[1]
    filename = sys.argv[2]
    process_base64_multipart_data_file(filename, boundary)
    return 0


if __name__ == "__main__":
    sys.exit(main())