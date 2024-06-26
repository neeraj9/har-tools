# Copyright (c) 2024 Neeraj Sharma
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import mimetypes

# ----------------------------------------------------------------------------
# Setup non-standard mime-types
# ----------------------------------------------------------------------------

# these mimetypes are non-standard, but used at various places

# usually its image/jpeg, see mimetypes.types_map for all known types
mimetypes.add_type("image/jpg", ".jpg")


def guess_extension(type_: str, strict: bool = True):
    return mimetypes.guess_extension(type_, strict)
