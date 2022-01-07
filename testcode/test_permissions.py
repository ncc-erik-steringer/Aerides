import unittest

from principalmapper.common import *
from principalmapper.querying import query_interface
from principalmapper.querying.presets.privesc import can_privesc
from principalmapper.util.storage import get_default_graph_path


class TestAuthorizationBoundaries(unittest.TestCase):

    def setUp(self) -> None:
        self.test_graph = Graph.create_graph_from_local_disk(get_default_graph_path('000000000000'))

    def test_no_privesc(self):
        for node in self.test_graph.nodes:
            if not node.is_admin:
                can_escalate, escalation_path = can_privesc(self.test_graph, node)
                self.assertFalse(
                    can_escalate,
                    '{} can priv-esc: {}'.format(
                        node.searchable_name(),
                        escalation_path
                    )
                )

    def test_support_cannot_put(self):
        s3_bucket_policies = []
        for policy in self.test_graph.policies:
            if 'arn:aws:s3' in policy.arn:
                s3_bucket_policies.append(policy)

        support_role = self.test_graph.get_node_by_searchable_name('role/support-staff')
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
                self.fail(
                    '{} is allowed to call s3:PutObject with {}'.format(
                        support_role.searchable_name(),
                        test_arn
                    )
                )

    def tearDown(self) -> None:
        del self.test_graph  # free up memory?


if __name__ == '__main__':
    unittest.main()
