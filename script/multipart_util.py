# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from util import (
    split_bytes_by_boundary,
    replace_non_alphanumeric,
    base64_decode_content,
)

from mimetype_util import (
    guess_extension
)

import os
from typing import Generator
from urllib.parse import unquote

# ----------------------------------------------------------------------------
# multipart functions 
# ----------------------------------------------------------------------------


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


def extract_multipart_data(decoded_data: bytes, boundary: bytes, index: int) -> Generator[tuple[str, bytes, str], None, None]:
    count = 0
    for part in split_bytes_by_boundary(decoded_data, boundary):
        result = parse_part(part)
        if result:
            (header, raw_data) = result
            content_type = header.get("content-type", "")
            extension = guess_extension(content_type)
            if not extension:
                extension = ".unknown"
            count += 1
            filename = f"{index}_file-{count}{extension}"
            for (key, value) in parse_content_disposition(header.get("content-disposition", "")):
                if key.strip().lower() == "name":
                    filename = f"{index}_{replace_non_alphanumeric(value)}{extension}"
                    break
            yield (filename, raw_data, content_type)


def process_multipart_data(data: bytes, boundary: str, index: int, extract=False, base64_encoded=False) -> Generator[tuple[str, bytes, str], None, None]:
    """Processes a data (optionally encoded in base64)."""
    decoded_data = base64_decode_content(data, base64_encoded)

    if extract and decoded_data:
        boundary_bytes = f"--{boundary}".encode("utf-8")
        for (output_filename, raw_data, content_type) in extract_multipart_data(decoded_data, boundary_bytes, index):
            yield (output_filename, raw_data, content_type)
