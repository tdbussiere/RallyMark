# Author: Tristan Bussiere <tristan@bussiere.dev>
# Version: 0.1
# Description: RallyMark allows the bulk-setting of test cases within a test set to a pre-determined value, among other features.

import getpass, os
from dotenv import load_dotenv
from pyral import Rally
from datetime import datetime

load_dotenv()

# File name for RallyMark to search for testcase:verdict pairs
verdict_file = 'test_verdicts.txt'

# Static metadata for test case results
result_notes = ""	# Unused currently
result_build = os.environ.get('rally_testcase_result_build')
result_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

# Define variables for Rally API access
server_domain = os.environ.get('rally_server_domain')

if server_domain == None:
    server_domain = "rally1.rallydev.com"

print('Using server %s.' % server_domain)

api_key = os.environ.get('rally_api_key')

if api_key == None:
    if os.environ.get('rally_username'):
        username = os.environ.get('rally_username')
        print('Logging in with username %s.' % username)
    else:
        username = input("Enter your Rally username:")

    if os.environ.get('rally_password'):
        password = os.environ.get('rally_password')
    else:
        password = getpass.getpass("Enter your Rally password:")

# String sanitization/normalization for formatted IDs

def normalize(formatted_ID):
    new = formatted_ID.upper()
    return new

def valid_formatted_id(formatted_id, prefix):

    # Return false if the string is less than three characters, doesn't have a prefix (i.e. TC, TS) or if the string following the prefix is not numeric
    if len(formatted_id) < 3 or formatted_id[:2] != prefix or formatted_id[3:].isnumeric() == False:
        return False

    return True

# Connect to Rally API
try:
    if api_key:
        rally = Rally(server=server_domain, apikey=api_key)
    else:
        rally = Rally(server=server_domain, user=username, password=password)

    # Query for and save the user ref here for later
    user_ref = rally.getUserInfo(username=username)[0].ref

except Exception as e:
    print('Error accessing the Rally WS API: %s' % e)
    exit()

print('Connected to Rally successfully. Authenticated as user ref [%s]' % user_ref)
test_set = normalize(input("Enter a test set ID (such as TS1111):"))

if valid_formatted_id(formatted_id=test_set, prefix='TS') == False:
    print('Invalid test set %s' % id)
    exit()

test_set = rally.get('TestSet', query='FormattedID = "%s"' % test_set)
try:
    test_set = test_set.next()
    print('Using test set %s' % test_set.Name)
except:
    print('Test set could not be located. Ensure it exists in your Rally workspace and try again.')
    exit()

# Get test case IDs from file
test_cases = []
with open(verdict_file, 'r') as f:

    for line in f:
        # Split the line into a test case formatted ID and a result
        case_id, verdict = line.strip().split(':')        
        case_id = normalize(case_id)

        if valid_formatted_id(formatted_id=case_id, prefix='TC') == False:
            print('Tesst case formatted ID is invalid: %s' % (case_id))
            continue

        test_cases.append((case_id,verdict))

success_count = 0

for case,verdict in test_cases:

    try:
        test_case = rally.get('TestCase', query='FormattedID = "%s"' % case).next()

        if test_case.Results != []:
            print('Test case %s already has at least one result; skipping.' % test_case.Name)
            continue

        result_info = { "testCase" : test_case.ref,
                      "date" : result_date,
                      "build" : result_build,
                      "testSet" : test_set.ref,
                      "verdict" : verdict,
                      "tester" : user_ref
                      }

        rally.put('TestCaseResult', result_info)

        success_count = success_count + 1
        print('Successfully updated test case %s (%s) with result \'%s\'' % (test_case.Name, test_case.FormattedID, verdict))

    except Exception as e:
        print("Error updating test case %s: %s" % (case, e))
        continue

print('RallyMark complete! Updated %d test cases.' % success_count)