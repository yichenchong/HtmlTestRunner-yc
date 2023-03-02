from unittest import TestCase, SkipTest
import contextlib
import sys

class SubTestSkippableCase(TestCase):

    @contextlib.contextmanager
    def testPartExecutor(self, test_case, isTest=False):
        super.testPartExecutor(self, test_case, isTest)
        if self.skipped[-1][0] == test_case and self.result_supports_subtests:
            self.errors.append((test_case, None))
            raise