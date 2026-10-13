import unittest
from evaluation.run import match_findings

class EvaluationTests(unittest.TestCase):
    def test_duplicate_prediction_cannot_receive_double_credit(self):
        expected=[{'category':'conflict','source_ids':['A','B']}]
        finding={'category':'conflict','evidence':[{'source_id':'B'},{'source_id':'A'}]}
        self.assertEqual(match_findings(expected,[finding,finding]),(1,1,0))

    def test_missing_side_does_not_match_conflict(self):
        self.assertEqual(match_findings([{'category':'conflict','source_ids':['A','B']}],[{'category':'conflict','evidence':[{'source_id':'A'}]}]),(0,1,1))

    def test_quiet_case_has_no_invented_score(self):
        self.assertEqual(match_findings([],[]),(0,0,0))
