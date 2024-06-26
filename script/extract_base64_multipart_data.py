# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


#
# python extract_base64_multipart_data.py "2f9825ee3f2949949f1210caa1978960" multipart.txt
#

from multipart_util import process_multipart_data

import os
import sys


# ----------------------------------------------------------------------------
# Process functions
# ----------------------------------------------------------------------------

def process_base64_multipart_data_file(filename: str, boundary: str):
    data = open(filename, "rb").read()
    if data.startswith(b"data:multipart/mixed;base64,"):
            data = data[len(b"data:multipart/mixed;base64,"):]
    for (output_filename, raw_data, content_type) in process_multipart_data(
            data, boundary, index=0, extract=True, base64_encoded=True):
            if not os.path.exists(output_filename):
                open(output_filename, "wb").write(raw_data)
                print(f"Writing filename = {output_filename}")
            else:
                print(f"Skip writing, filename = {output_filename} exists.")


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