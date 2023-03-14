# RallyMark
RallyMark is a Python application that marks Rally test cases with a pre-determined verdict. You should add test cases and verdicts as key:value pairs in the `test_verdicts.txt` file, for example: `tc123456:pass`, one test case per line.

RallyMark only adds new results if a test case does not already have a result.

## Getting Started

1. Install Python 3.
2. Install all required packages: `pip install -r requirements.txt`
3. Rename the `.env.example` file to `.env` and change the values as needed. There are variables for Rally authentication via API key or username and password, test result build, and optionally you may change the server that RallyMark uses.
4. Add test case IDs (TC#) and corresponding verdicts to the test_verdicts.txt file. For example, TC123456:pass. Each test case should be separated by a single line. Test case IDs will be validated and skipped if they are malformed or don't exist in the workspace.
5. Run the script: `python main.py`
6. Once authenticated, provide a test set ID (TS#) for test results to be attached to.

## Notes

* RallyMark will skip test cases that already have results.
* RallyMark will skip the currently processing test case, but not abort, if the test case is malformed or does not exist.
* Currently cannot run without a test set. All test case results must be attached to a test set.
* RallyMark will use the current user to set the `Tester` field. Currently in API mode this does not work and will be fixed soon.
* Untested on macOS.