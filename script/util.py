# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import base64
import re


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


def base64_decode_content(content: bytes, base64_encoded=False) -> bytes:
    try:
        if base64_encoded:
            return base64.b64decode(content)
        else:
            return content
    except base64.binascii.Error:
        print(f"Error: Invalid base64 encoding")
        return content