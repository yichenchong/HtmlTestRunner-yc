from unittest import TestCase
from unittest.case import _Outcome

class SubTestSkippableCase(TestCase):
    def __init__(self, methodName='runTest'):
        self().__init__(methodName)
        self.methodName = methodName
        self.skip_errors = []

    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            stopTestRun = getattr(result, 'stopTestRun', None)
            if startTestRun is not None:
                startTestRun()
        else:
            stopTestRun = None

        result.startTest(self)
        try:
            testMethod = getattr(self, self.methodName)
            if (getattr(self.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
                # If the class or method was skipped.
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                self._addSkip(result, self, skip_why)
                return result

            expecting_failure = (
                getattr(self, "__unittest_expecting_failure__", False) or
                getattr(testMethod, "__unittest_expecting_failure__", False)
            )
            outcome = _Outcome(result)
            try:
                self._outcome = outcome

                with outcome.testPartExecutor(self):
                    self._callSetUp()
                if outcome.success:
                    outcome.expecting_failure = expecting_failure
                    with outcome.testPartExecutor(self, isTest=True):
                        self._callTestMethod(testMethod)
                    outcome.expecting_failure = False
                    with outcome.testPartExecutor(self):
                        self._callTearDown()

                self.doCleanups()
                for test, reason in outcome.skipped:
                    self.skip_errors.append(test, [])
                    self._addSkip(result, test, reason)
                self._feedErrorsToResult(result, outcome.errors)
                self._feedErrorsToResult(result, self.skip_errors)
                if outcome.success:
                    if expecting_failure:
                        if outcome.expectedFailure:
                            self._addExpectedFailure(result, outcome.expectedFailure)
                        else:
                            self._addUnexpectedSuccess(result)
                    else:
                        result.addSuccess(self)
                return result
            finally:
                # explicitly break reference cycles:
                # outcome.errors -> frame -> outcome -> outcome.errors
                # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
                outcome.errors.clear()
                outcome.expectedFailure = None

                # clear the outcome, no more needed
                self._outcome = None
        finally:
            result.stopTest(self)
            if stopTestRun is not None:
                stopTestRun()