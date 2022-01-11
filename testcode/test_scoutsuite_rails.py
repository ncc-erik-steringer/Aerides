#  Copyright (c) 2022 Erik Steringer and NCC Group
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import json
from typing import Optional, Union
import unittest


def _get_item(ptr, itempath: str) -> Union[str, dict, list, None]:
    """Utility function. The ptr param should point at .services then follow the itempath (separated via '.') to
    the expected object. Returns None if invalid (tries to avoid Error)."""
    root = ptr
    for element in itempath.split('.'):
        if isinstance(root, dict):
            if element in root:
                root = root[element]
            else:
                return None
        elif isinstance(root, list):
            index = int(element)
            if not (0 <= index < len(root)):
                return None
            root = root[index]
        else:
            return None
    return root


class TestScoutSuiteExpected(unittest.TestCase):

    def setUp(self) -> None:
        # per https://github.com/nccgroup/ScoutSuite/wiki/Exporting-and-Programmatically-Accessing-the-Report

        with open('/tmp/artifacts/scout-dir/scoutsuite-results/scoutsuite_results_aws-000000000000.js') as fd:
            fd.readline()  # discard first line
            self.scoutdata = json.load(fd)  # type: dict

    def test_ec2_no_ports_open_to_all(self):
        # Verify that none of the security groups have a port open to 0.0.0.0/0

        # start by grabbing a handle to the .services.ec2.findings dict
        ptr = self.scoutdata.get('services', {})
        ptr = ptr.get('ec2', {})
        ptr = ptr.get('findings')  # type: Optional[dict]
        if ptr is None:
            return

        # look at all findings for "port is open", group them up, report
        issues = []
        for finding, data in ptr.items():
            if 'ec2-security-group-opens' not in finding or 'port-to-all' not in finding:
                continue

            if data['flagged_items'] > 0:
                issues.append((finding, data))

        if len(issues) > 0:
            self.fail(
                'ScoutSuite reported the following EC2 Security Group findings:\n\n{}'.format(
                    '\n\n'.join(
                        ['{}\n{}'.format(x, '\n'.join(y['items'])) for x, y in issues]
                    )
                )
            )

    def test_iam_no_inline_passrole(self):
        """Verify there are no inline policies granting iam:PassRole for *"""

        # get the handle
        ptr = self.scoutdata.get('services', {})
        ptr = ptr.get('iam', {})
        ptr = ptr.get('findings')  # type: Optional[dict]
        if ptr is None:
            return

        # Review all iam-PassRole findings
        finding_names = (
            'iam-inline-role-policy-allows-iam-PassRole',
            'iam-inline-user-policy-allows-iam-PassRole',
            'iam-inline-group-policy-allows-iam-PassRole'
        )
        finding_items = []

        for finding_name in finding_names:
            finding_contents = ptr.get(finding_name)
            if finding_contents is not None:
                finding_items.extend(finding_contents['items'])

        if len(finding_items) > 0:
            item_listing = []
            for item in finding_items:
                root = self.scoutdata.get('services')
                item_ref = _get_item(root, '.'.join(item.split('.')[:3]))  # type: Optional[dict]
                if item_ref is not None:
                    item_listing.append(item_ref.get('arn'))
                else:
                    item_listing.append(item)
            self.fail(
                'The following IAM Users/Roles/Groups had an inline policy allowing '
                'iam:PassRole for all resources:\n\n{}'.format(
                    '\n'.join(['* {}'.format(x) for x in item_listing])
                )
            )

    def test_iam_no_inline_notaction(self):
        # Verify no inline IAM Policies (for Users/Roles/Groups) use the NotAction field

        # get the handle
        ptr = self.scoutdata.get('services', {})
        ptr = ptr.get('iam', {})
        ptr = ptr.get('findings')  # type: Optional[dict]
        if ptr is None:
            return

        # Review all iam-PassRole findings
        finding_names = (
            'iam-inline-role-policy-allows-NotActions',
            'iam-inline-user-policy-allows-NotActions',
            'iam-inline-group-policy-allows-NotActions'
        )
        finding_items = []

        for finding_name in finding_names:
            finding_contents = ptr.get(finding_name)
            if finding_contents is not None:
                finding_items.extend(finding_contents['items'])

        if len(finding_items) > 0:
            item_listing = []
            for item in finding_items:
                root = self.scoutdata.get('services')
                item_ref = _get_item(root, '.'.join(item.split('.')[:3]))  # type: Optional[dict]
                if item_ref is not None:
                    item_listing.append(item_ref.get('arn'))
                else:
                    item_listing.append(item)
            self.fail(
                'The following IAM Users/Roles/Groups had an inline policy that uses '
                'NotAction in a statement:\n\n{}'.format(
                    '\n'.join(['* {}'.format(x) for x in item_listing])
                )
            )

    def tearDown(self) -> None:
        del self.scoutdata
