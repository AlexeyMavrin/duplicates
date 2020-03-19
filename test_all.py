"""Execute entire unit test suite. Run all the tests.
"""

# Note: to run this from the shell
# python3 -m unittest discover -p 'test_*.py' -s $(dirname $0)
import unittest


def main():
    tests = unittest.TestLoader().discover('.')
    ret = unittest.TextTestRunner(verbosity=1).run(tests)
    return len(ret.failures)  # the error code is the number of errors or 0 for ok


if __name__ == "__main__":
    exit(main())
