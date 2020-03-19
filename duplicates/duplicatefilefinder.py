#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for traversing a directory structure, finding duplicate FILES and displaying them,
but does NOT delete them."""

import hashlib
import os
import zlib
from functools import reduce, partial

from duplicates import UpdatePrinter

__author__ = "Michael Krisper"
__copyright__ = "Copyright 2012, Michael Krisper"
__credits__ = ["Michael Krisper"]
__license__ = "GPL"
__version__ = "1.3.1"
__maintainer__ = "Michael Krisper"
__email__ = "michael.krisper@gmail.com"
__status__ = "Production"
__python_version__ = "2.7.3"


def get_hash_key(filename):
    """Calculates the hash value for a file."""
    hash_object = hashlib.sha256()
    with open(filename, 'rb') as input_file:
        for chunk in iter(partial(input_file.read, 1024 * 8), b""):
            hash_object.update(chunk)
    return hash_object.digest()


def get_crc_key(filename):
    """Calculates the crc value for a file."""
    with open(filename, 'rb') as input_file:
        chunk = input_file.read(1024)
    return zlib.adler32(chunk)


def filter_duplicate_files(files, top=None):
    """Finds all duplicate files in the directory."""
    duplicates = {}
    update = UpdatePrinter.UpdatePrinter().update
    iterations = ((os.path.getsize, "By Size", top ** 2 if top else None),
                  # top * top <-- this could be performance optimized further by top*3 or top*4
                  (get_crc_key, "By CRC ", top * 2 if top else None),  # top * 2
                  (get_hash_key, "By Hash", None))

    for key_function, name, top_count in iterations:
        duplicates.clear()
        count = 0
        duplicate_count = 0
        i = 0
        for i, file_path in enumerate(files, start=1):
            key = key_function(file_path)
            duplicates.setdefault(key, []).append(file_path)
            if len(duplicates[key]) > 1:
                count += 1
                if len(duplicates[key]) == 2:
                    count += 1
                    duplicate_count += 1

            update("\r(%s) %d Files checked, %d duplicates found (%d files)" % (name, i, duplicate_count, count))
        else:
            update("\r(%s) %d Files checked, %d duplicates found (%d files)" % (name, i, duplicate_count, count),
                   force=True)
        print("")
        sorted_files = sorted(iter(duplicates.values()), key=len, reverse=True)
        files = [file_path for file_paths in sorted_files[:top_count] if len(file_paths) > 1 for file_path in
                 file_paths]

    return [file_list for file_list in duplicates.values() if len(file_list) > 1]


def get_files(directory, include_hidden, include_empty):
    """Returns all FILES in the directory which apply to the filter rules."""
    return (os.path.join(dir_path, filename)
            for dir_path, _, file_names in os.walk(directory)
            for filename in file_names
            if not os.path.islink(os.path.join(dir_path, filename))
            and (include_hidden or
                 reduce(lambda r, d: r and not d.startswith("."),
                        os.path.abspath(os.path.join(dir_path, filename)).split(os.sep), True))
            and (include_empty or os.path.getsize(os.path.join(dir_path, filename)) > 0))
