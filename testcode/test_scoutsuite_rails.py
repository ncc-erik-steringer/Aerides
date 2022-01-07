import json
import unittest


class TestScoutSuiteExpected(unittest.TestCase):

    def setUp(self) -> None:
        # per https://github.com/nccgroup/ScoutSuite/wiki/Exporting-and-Programmatically-Accessing-the-Report

        with open('./scoutsuite-report/scoutsuite-results/scoutsuite_results_aws-000000000000.js') as fd:
            fd.readline()  # discard first line
            self.scoutdata = json.load(fd)  # type: dict

    def test_ec2_no_ports_open_to_all(self):
        # Verify that none of the security groups have a port open to 0.0.0.0/0

        # start by grabbing a handle to the .services.ec2.findings dict
        ptr = self.scoutdata.get('services', {})
        ptr = ptr.get('ec2', {})
        ptr = ptr.get('findings')
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

    def test_iam_no_inline_notaction(self):
        # Verify no inline IAM Policies (for Users/Roles/Groups) use the NotAction field

        # start by getting a handle to the .services.iam.findings dict
        ptr = self.scoutdata.get('services', {})
        ptr = ptr.get('iam', {})
        ptr = ptr.get('findings')
        if ptr is None:
            return

        # look at each of the NotAction findings
        inline_group_policy_finding = ptr.get('iam-inline-group-policy-allows-NotActions')
        if inline_group_policy_finding is not None:
            if inline_group_policy_finding['flagged_items'] > 0:
                self.fail(
                    'IAM Group Inline Policy/Policies had NotAction Element:\n\n{}'.format(
                        '\n'.join(['* {}'.format(x) for x in inline_group_policy_finding.get('items')])
                    )
                )

        inline_role_policy_finding = ptr.get('iam-inline-role-policy-allows-NotActions')
        if inline_role_policy_finding is not None:
            if inline_role_policy_finding['flagged_items'] > 0:
                self.fail(
                    'IAM Role Inline Policy/Policies had NotAction Element:\n\n{}'.format(
                        '\n'.join(['* {}'.format(x) for x in inline_role_policy_finding.get('items')])
                    )
                )

        inline_user_policy_finding = ptr.get('iam-inline-user-policy-allows-NotActions')
        if inline_user_policy_finding is not None:
            if inline_user_policy_finding['flagged_items'] > 0:
                self.fail(
                    'IAM User Inline Policy/Policies had NotAction Element:\n\n{}'.format(
                        '\n'.join(['* {}'.format(x) for x in inline_user_policy_finding.get('items')])
                    )
                )

    def tearDown(self) -> None:
        del self.scoutdata
