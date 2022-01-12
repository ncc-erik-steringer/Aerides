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

from typing import List, Tuple, Optional
import unittest

from principalmapper.common import *
from principalmapper.querying import query_interface
from principalmapper.querying.presets.privesc import can_privesc
from principalmapper.util.storage import get_default_graph_path


class TestAuthorizationBoundaries(unittest.TestCase):

    def setUp(self) -> None:
        self.test_graph = Graph.create_graph_from_local_disk(get_default_graph_path('000000000000'))

    def test_no_privesc(self):
        """Ensure that nobody can escalate their privileges from non-admin to to admin."""
        privesc_paths = []  # type: List[Tuple[Node, List[Edge]]]
        for node in self.test_graph.nodes:
            if not node.is_admin:
                can_escalate, escalation_path = can_privesc(self.test_graph, node)
                if can_escalate:
                    privesc_paths.append((node, escalation_path))

        if len(privesc_paths) > 0:
            self.fail(
                'Privilege escalation risks detected:\n\n{}'.format(
                    '\n'.join(
                        ['* {}'.format(', '.join([x.describe_edge() for x in path])) for node, path in privesc_paths]
                    )
                )
            )

    def test_support_cannot_put(self):
        """Ensure that the IAM Role named 'support-staff' cannot call s3:PutObject for any of the S3 buckets."""

        s3_bucket_policies = []
        for policy in self.test_graph.policies:
            if 'arn:aws:s3' in policy.arn:
                s3_bucket_policies.append(policy)

        support_role = self.test_graph.get_node_by_searchable_name('role/support-staff')

        violations = []
        for s3_bucket_policy in s3_bucket_policies:
            test_arn = s3_bucket_policy.arn + '/test_object'
            result = query_interface.search_authorization_full(
                self.test_graph,
                support_role,
                's3:PutObject',
                test_arn,
                {},
                s3_bucket_policy.policy_doc,
                '000000000000'
            )
            if result.allowed:
                violations.append('{} is allowed to call s3:PutObject for {}'.format(
                    support_role.searchable_name(),
                    test_arn
                ))

        if len(violations) > 0:
            self.fail('Support was allowed to upload files to S3:\n\n{}'.format(
                '\n'.join(['* {}'.format(x) for x in violations])
            ))

    def test_support_has_no_edges(self):
        """Ensure that the IAM Role named 'support-staff' cannot access any other users or roles in the account."""

        support_edges = []  # type: List[Edge]
        for edge in self.test_graph.edges:
            if edge.source.searchable_name() == 'role/support-staff':
                support_edges.append(edge)

        if len(support_edges) > 0:
            self.fail('The support staff role had access to other users or roles in the account:\n\n{}'.format(
                '\n'.join(
                    [edge.describe_edge() for edge in support_edges]
                )
            ))

    def tearDown(self) -> None:
        del self.test_graph  # free up memory?


if __name__ == '__main__':
    unittest.main()
