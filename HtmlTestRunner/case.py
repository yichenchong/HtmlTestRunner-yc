from unittest import TestCase, SkipTest

class SubTestSkippableCase(TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.skip_errors = []

    def run(self, result=None):
        if result is None:
            result = super.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            stopTestRun = getattr(result, 'stopTestRun', None)
            if startTestRun is not None:
                startTestRun()
        else:
            stopTestRun = None

        result.startTest(super)
        try:
            testMethod = getattr(super, super._testMethodName)
            if (getattr(super.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
                # If the class or method was skipped.
                skip_why = (getattr(super.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                super._addSkip(result, super, skip_why)
                return result

            expecting_failure = (
                getattr(super, "__unittest_expecting_failure__", False) or
                getattr(testMethod, "__unittest_expecting_failure__", False)
            )
            outcome = super._Outcome(result)
            try:
                super._outcome = outcome

                with outcome.testPartExecutor(super):
                    super._callSetUp()
                if outcome.success:
                    outcome.expecting_failure = expecting_failure
                    with outcome.testPartExecutor(super, isTest=True):
                        super._callTestMethod(testMethod)
                    outcome.expecting_failure = False
                    with outcome.testPartExecutor(super):
                        super._callTearDown()

                super.doCleanups()
                for test, reason in outcome.skipped:
                    exc_info = []
                    self.skip_errors.append(test, [])
                    super._addSkip(result, test, reason)
                super._feedErrorsToResult(result, outcome.errors)
                super._feedErrorsToResult(result, self.skip_errors)
                if outcome.success:
                    if expecting_failure:
                        if outcome.expectedFailure:
                            super._addExpectedFailure(result, outcome.expectedFailure)
                        else:
                            super._addUnexpectedSuccess(result)
                    else:
                        result.addSuccess(super)
                return result
            finally:
                # explicitly break reference cycles:
                # outcome.errors -> frame -> outcome -> outcome.errors
                # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
                outcome.errors.clear()
                outcome.expectedFailure = None

                # clear the outcome, no more needed
                super._outcome = None

        finally:
            result.stopTest(super)
            if stopTestRun is not None:
                stopTestRun()