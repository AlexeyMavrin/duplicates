"""
Created on Feb 3, 2018

@author: "Alexey Mavrin"
@email alexeymavrin@gmail.com
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from itertools import chain
from time import ctime
from traceback import print_exc

import humanize

from duplicates.duplicatefilefinder import get_files, filter_duplicate_files

logging.basicConfig()
logger = logging.getLogger("duplicates")


# CUSTOM EXCEPTIONS/ Classes
class ArgumentCheck(BaseException):
    pass


class Stats(object):
    """ Statistics class """

    def __init__(self):
        self.total_files = 0
        self.keep_files = 0
        self.skipped_files = 0
        self.to_delete_files = 0
        self.deleted_files = 0

    def __repr__(self):
        return "Total duplicates: %i, keep: %i, skipped (in golden): %i, deleted: %i/%i" % (
            self.keep_files + self.skipped_files + self.to_delete_files,
            self.keep_files,
            self.skipped_files,
            self.deleted_files,
            self.to_delete_files)


def parse_arguments():
    """ Parses the arguments """
    description = ("Finds duplicates in both `work` and `golden` folders. \n"
                   "Duplicates that are in `work` folder are purged. \n"
                   "Trying to keep an oldest file.")
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=description)
    parser.add_argument('-v', '--verbose', help='display debug info', action='store_true')
    parser.add_argument('-g', '--golden',
                        help='(optional) path to the folder where duplicates will be searched though this folder will '
                             'be unchanged',
                        required=False)
    parser.add_argument('-w', '--work',
                        help='work folder that will be stripped from the duplicates found in both itself and `golden`',
                        required=True)
    parser.add_argument('-p', '--purge',
                        help='purge/ delete extra files from `work` folder. '
                             'If all copies are under work, single (with oldest '
                             'modification time) file will be preserved. All duplicates in golden also '
                             'preserved/skipped.',
                        action='store_true')

    args, unparsed = parser.parse_known_args()
    if unparsed:
        raise Exception("Unknown arguments: %s" % unparsed)

    parse_arguments.ARGS = args
    return parse_arguments.ARGS


def get_all_files(path, ignore=None):
    """get all files including hidden"""
    all_files = []
    if ignore is None:
        ignore = []
    for root, _, files in os.walk(path):
        for filename in files:
            if filename not in ignore:
                all_files.append(os.path.join(root, filename))
    return all_files


def print_and_process_duplicates(files, golden, purge=False):
    """ Prints a list of duplicates.
    Pretty much the same as duplicate file finder however modified not to sort duplicated files"""
    # sort high level; by their size and then by number of duplicated files
    sorted_files = sorted(files, key=lambda x: (os.path.getsize(x[0]), len(x)), reverse=True)
    # now sort duplicate lists for each duplicate according 1. if it is in golden and modification date
    sorted_files = [
        sorted(paths, key=lambda x: (not (x + os.sep).startswith(golden + os.sep), os.path.getmtime(x)), reverse=False)
        for paths in sorted_files]

    # statistics
    stats = Stats()

    for pos, paths in enumerate(sorted_files, start=1):
        prefix = os.path.dirname(os.path.commonprefix(paths))
        if len(prefix) == 1:
            prefix = ""

        try:
            size_ = humanize.naturalsize(os.path.getsize(paths[0]), gnu=True)
        except OSError as e:
            size_ = e
        print("\n(%d) Found %d duplicate files (size: %s) in '%s/':" % (pos, len(paths), size_, prefix))

        # fill the tags
        tags = ["NA"] * len(paths)  # mark with NA
        tags[0] = " K"  # keep the first one in our sorted list
        for i, t in enumerate(paths[1:], start=1):
            tags[i] = " S" if (t + os.sep).startswith(golden + os.sep) else "*D"

        stats.keep_files += tags.count(" K")
        stats.skipped_files += tags.count(" S")
        stats.to_delete_files += tags.count("*D")

        # redundant checks - just to be super cautious
        if len(tags) != len(paths):
            raise Exception("something wrong - should never trigger - tags mismatch")
        if tags.count("*D") >= len(tags):
            raise Exception("something wrong - should never trigger - tags counter mismatch")
        if len(tags) <= 1:
            raise Exception("something wrong - should never trigger - tags min. len. mismatch")

        for i, (tag, path) in enumerate(zip(tags, paths), start=1):
            try:
                file_time = ctime(os.path.getmtime(os.path.join(prefix, path)))
            except OSError as e:
                file_time = e

            print("%2d: %2s '%s' [%s]" % (i, tag, path[len(prefix) + 1:].strip(), file_time), end='')
            if purge and tag == "*D":
                try:
                    os.unlink(os.path.join(prefix, path))
                    stats.deleted_files += 1
                    print(" - DELETED")
                except OSError as e:
                    print("ERROR: ", e)
            else:
                print()

    return stats


def duplicates(work, golden=None, purge=False):
    """ Finds duplicates and purges them based on the flags
    @param work: work path where duplicates will be searched and purged if purge flag is set
    @param golden: path where duplicates will be searched, however never deleted
    @param purge: delete duplicates, keep single copy only (files in golden preserved)
    @return: statistics object
    """

    # 1. optimization checks
    if golden:
        golden = os.path.abspath(golden)
        print("files unchanged (golden) in:", golden)
    else:
        golden = "\x00"  # if golden is not set, make it non path string
    work = os.path.abspath(work)
    print("searching and removing duplicates in:", work)

    if (work + os.sep).startswith(golden + os.sep):
        raise ArgumentCheck("work path is under golden")

    # 2. find duplicates
    all_files = get_files(directory=work, include_hidden=True, include_empty=True)
    if golden != "\x00":  # add golden generator
        all_files = chain(all_files, get_files(directory=golden, include_hidden=True,
                                               include_empty=True))
    duplicate_lists = filter_duplicate_files(all_files, None)

    # 3. print the results and purge duplicates if needed
    stats = print_and_process_duplicates(duplicate_lists, golden, purge)

    # 4. Another redundant check
    if sum([len(x) for x in duplicate_lists]) != stats.keep_files + stats.skipped_files + stats.to_delete_files:
        raise Exception("Hmm should never get here, data verification failed")

    # 5. remove empty dirs in work
    if purge:
        print("Deleting empty dir's in work ('%s')" % work)
        delete_empty_dirs(work)

    return stats


def main():
    """ The main function"""

    try:
        # *** Execution time ***
        started = datetime.now()

        # 0. get arguments
        args = parse_arguments()

        # 1. prepare
        logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

        # 2. duplicates
        stats = duplicates(args.work, args.golden, args.purge)
        print(stats)

        # *** EXECUTION TIME ***
        ended = datetime.now()
        print('Complete in %i minutes (%i sec.).' % ((ended - started).seconds / 60, (ended - started).seconds))
        return 0

    except KeyboardInterrupt:
        logger.error("terminated by user")
        sys.exit(1)

    except Exception as e:
        if logger.level == logging.DEBUG:
            print_exc(file=sys.stderr)
        logger.error(e)
        sys.exit(2)


def delete_empty_dirs(path):
    """ Recursively remove empty directories """
    for root, dirs, files in os.walk(str(path)):
        # remover osX hidden files
        if len(files) == 1:
            try:
                os.unlink(os.path.join(root, ".DS_Store"))
            except OSError:
                pass

        # recursion
        for dir_ in dirs:
            delete_empty_dirs(os.path.join(root, dir_))
            try:
                os.rmdir(os.path.join(root, dir_))  # deletes only empty dirs
                print("   empty directory removed: ", os.path.join(root, dir_).encode('utf-8'))
            except OSError:
                pass

    # print root


if __name__ == '__main__':
    main()
