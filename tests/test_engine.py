import copy
import json
from pathlib import Path
import unittest
from engine import analyze, validate_report

SOURCES = json.loads((Path(__file__).resolve().parents[1] / 'data/scenarios.json').read_text())[0]['sources']

class EvidenceTests(unittest.TestCase):
    def test_unknown_source_rejected(self):
        report = analyze(SOURCES, 'replay')['report']
        report['findings'][0]['evidence'][0]['source_id'] = 'invented'
        with self.assertRaises(ValueError):
            validate_report(report, SOURCES)

    def test_fabricated_quote_rejected(self):
        report = analyze(SOURCES, 'replay')['report']
        report['findings'][0]['evidence'][0]['quote'] = 'All equipment safe'
        with self.assertRaises(ValueError):
            validate_report(report, SOURCES)

    def test_absent_evidence_rejected(self):
        report = analyze(SOURCES, 'replay')['report']
        report['findings'][0]['evidence'] = []
        with self.assertRaises(ValueError):
            validate_report(report, SOURCES)

    def test_duplicate_sources_rejected(self):
        with self.assertRaises(ValueError):
            analyze(SOURCES + [copy.deepcopy(SOURCES[0])], 'replay')

    def test_routine_case_has_no_rule_findings(self):
        scenarios = json.loads((Path(__file__).resolve().parents[1] / 'data/scenarios.json').read_text())
        self.assertEqual(analyze(scenarios[1]['sources'], 'replay')['report']['findings'], [])

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):
            analyze(SOURCES, 'other')

if __name__ == '__main__':
    unittest.main()
