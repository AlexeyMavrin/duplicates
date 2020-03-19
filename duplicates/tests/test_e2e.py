"""
Created on Jan 23, 2018

@author: alexeymavrin@gmail.com

"""

import os
import shutil
import sys
import unittest
from io import StringIO

from duplicates import duplicates


class DuplicatesE2EValidation(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.path.abspath(os.curdir)
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        # save stdout to a variable
        self.stdout_orig = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout
        self.argv = sys.argv  # preserve arguments

        # copy sample to tst
        shutil.rmtree("unsorted", ignore_errors=True)
        shutil.rmtree("tgt", ignore_errors=True)
        shutil.rmtree("tst", ignore_errors=True)
        shutil.copytree("sample", "tst")

    def tearDown(self):
        sys.stdout = self.stdout_orig
        sys.argv = self.argv  # restore arguments
        # print self.stdout.getvalue().strip()

        # clear tst
        shutil.rmtree("unsorted", ignore_errors=True)
        shutil.rmtree("tst")
        shutil.rmtree("tgt", ignore_errors=True)
        shutil.rmtree("tst copy", ignore_errors=True)

        os.chdir(self.current_dir)

    def test_straight(self):
        """Test that duplicates.py finds all the duplicates in the sample folder"""

        sys.argv = ['-v', '-g', os.path.join('tst', 'golden'), '-w', os.path.join('tst', 'work'), '--purge']

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")
        # print len(all_files), all_files

        # 1. find all duplicates
        # with self.assertRaises(duplicates.GreatSuccess):
        # duplicates.main()
        duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(8, len(all_files), "total files")

        all_files = duplicates.get_all_files("tst/work")
        # print len(all_files), all_files
        self.assertEqual(1, len(all_files), "total files")

        all_files = duplicates.get_all_files("tst/golden")
        # print len(all_files), all_files
        self.assertEqual(5, len(all_files), "total files")

    def test_reverse(self):
        """Make sure that the golden would not change - test wise versa"""

        sys.argv = ['-v', '-w', os.path.join('tst', 'golden'), '-g', os.path.join('tst', 'work'), "-p"]

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")
        # print len(all_files), all_files

        all_files = duplicates.get_all_files("tst/work")
        self.assertEqual(9, len(all_files), "total files")
        # print len(all_files), all_files

        # 1. find all duplicates
        # with self.assertRaises(duplicates.GreatSuccess):
        # duplicates.main()
        duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(12, len(all_files), "total files")

        all_files = duplicates.get_all_files("tst/work")
        # print len(all_files), all_files
        self.assertEqual(9, len(all_files), "total files")

        all_files = duplicates.get_all_files("tst/golden")
        # print len(all_files), all_files
        self.assertEqual(1, len(all_files), "total files")

    def test_path(self):
        """What if work is in golden"""

        sys.argv = ['-v', '-g', os.path.join('tst', ''), '-w', os.path.join('tst', 'work')]

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")

        # find all duplicates
        with self.assertRaises(duplicates.ArgumentCheck):
            duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")

    def test_path_same(self):
        """What if work is in golden (same path)"""

        sys.argv = ['-v', '-g', os.path.join('tst', ''), '-w', os.path.join('tst', '')]

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")

        # find all duplicates
        with self.assertRaises(duplicates.ArgumentCheck):
            duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")

    def test_path2(self):
        """What if golden is in work"""

        sys.argv = ['-v', '-w', os.path.join('tst', ''), '-g', os.path.join('tst', 'golden'), "-p"]

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files before")

        # find all duplicates
        # with self.assertRaises(duplicates.GreatSuccess):
        # duplicates.main()
        duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(7, len(all_files), "total files after")

        all_files = duplicates.get_all_files("tst/work")
        self.assertEqual(1, len(all_files), "files in work")

        all_files = duplicates.get_all_files("tst/golden")
        self.assertEqual(5, len(all_files), "files in work")

    def test_date1(self):
        """Make sure we preserve the oldest"""

        sys.argv = ['-v', '-w', os.path.join('tst', ''), '-g', os.path.join('tst', 'golden'), '-p']

        # change modify time
        tfn = 'tst/work/1/.new.jpg'
        self.assertTrue(os.path.isfile(tfn), '%s exists' % tfn)
        os.utime(tfn, (0, 0))
        duplicates.main()

        self.assertTrue(os.path.isfile(tfn), '%s exists' % tfn)

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(7, len(all_files), "total files after")

    def test_date2(self):
        """Make sure to remove most recent"""

        sys.argv = ['-v', '-w', os.path.join('tst', ''), '-g', os.path.join('tst', 'golden'), "-p"]

        # change modify time
        tfn = 'tst/work/1/.new.jpg'
        self.assertTrue(os.path.isfile(tfn), '%s exists' % tfn)
        file_time = os.path.getmtime(tfn)
        os.utime(tfn, (file_time * 2, file_time * 2))
        duplicates.main()

        self.assertFalse(os.path.isfile(tfn), '%s exists' % tfn)

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(7, len(all_files), "total files after")

    def test_no_golden(self):
        """Make sure we keep one good version in work if golden is not given"""

        sys.argv = ['-v', '-w', os.path.join('tst', ''), "-p"]

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")

        # 1. find all duplicates
        # with self.assertRaises(duplicates.GreatSuccess):
        # duplicates.main()
        duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(6, len(all_files), "total files")

    def test_duplicates_similar_names(self):
        """Similar names test"""

        sys.argv = ['-v', '-w', os.path.join('tst copy', ''), '-g', os.path.join('tst', ''), "-p"]

        shutil.rmtree("tst copy", ignore_errors=True)
        shutil.copytree("sample", "tst copy", )

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")
        all_files = duplicates.get_all_files("tst copy")
        self.assertEqual(16, len(all_files), "total files")

        duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")

        all_files = duplicates.get_all_files("tst copy")
        self.assertEqual(0, len(all_files), "total files")

    def test_duplicates_similar_names2(self):
        """Similar names the other way around"""

        sys.argv = ['-v', '-g', os.path.join('tst copy', ''), '-w', os.path.join('tst', ''), "-p"]

        shutil.rmtree("tst copy", ignore_errors=True)
        shutil.copytree("sample", "tst copy", )

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(16, len(all_files), "total files")
        all_files = duplicates.get_all_files("tst copy")
        self.assertEqual(16, len(all_files), "total files")

        duplicates.main()

        all_files = duplicates.get_all_files("tst")
        self.assertEqual(0, len(all_files), "total files")

        all_files = duplicates.get_all_files("tst copy")
        self.assertEqual(16, len(all_files), "total files")


def main():
    tests = unittest.TestLoader().discover('')
    ret = unittest.TextTestRunner(verbosity=1).run(tests)
    return len(ret.failures)


if __name__ == '__main__':
    exit(main())
