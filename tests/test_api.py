import json
import os
import unittest
from unittest.mock import patch
from app import app
from engine import validate_report, analyze, ModelResponseError
from test_engine import SOURCES

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client=app.test_client()

    def test_baseline_end_to_end(self):
        response=self.client.post('/api/analyze',json={'sources':SOURCES,'mode':'replay'})
        self.assertEqual(response.status_code,200)
        data=response.get_json()
        self.assertEqual(data['mode'],'replay')
        self.assertIsNone(data['model'])
        self.assertEqual(data['sources'],SOURCES)
        self.assertEqual(len(data['source_digest']),64)
        self.assertEqual([f['id'] for f in data['report']['findings']],['F-01','F-02'])

    def test_disabled_gemini_cannot_silently_fallback(self):
        with patch.dict(os.environ,{'ENABLE_GEMINI':'0'}):
            response=self.client.post('/api/analyze',json={'sources':SOURCES,'mode':'gemini'})
        self.assertEqual(response.status_code,503)
        self.assertNotIn('report',response.get_json())

    def test_oversized_payload(self):
        response=self.client.post('/api/analyze',data=json.dumps({'x':'x'*65000}),content_type='application/json')
        self.assertEqual(response.status_code,413)

    def test_bad_json(self):
        response=self.client.post('/api/analyze',data='{',content_type='application/json')
        self.assertEqual(response.status_code,400)

    def test_invalid_model_output_is_upstream_error(self):
        with patch.dict(os.environ,{'ENABLE_GEMINI':'1','GOOGLE_CLOUD_PROJECT':'offline','GEMINI_MODEL':'offline'}), patch('app.analyze',side_effect=ModelResponseError('invalid')):
            response=self.client.post('/api/analyze',json={'sources':SOURCES,'mode':'gemini'})
        self.assertEqual(response.status_code,502)
        self.assertNotIn('report',response.get_json())

    def test_one_sided_conflict_rejected(self):
        report=analyze(SOURCES,'replay')['report']
        report['findings'][0]['category']='conflict'
        with self.assertRaises(ValueError):validate_report(report,SOURCES)

    def test_changed_sources_change_fingerprint(self):
        changed=[dict(s) for s in SOURCES]
        changed[0]['text']+=' Correction recorded.'
        self.assertNotEqual(analyze(SOURCES,'replay')['source_digest'],analyze(changed,'replay')['source_digest'])

    def test_sdk_accepts_schema_and_cloud_client(self):
        from google import genai
        from google.genai import types
        from google.auth.credentials import AnonymousCredentials
        from engine import SCHEMA
        config=types.GenerateContentConfig(response_mime_type='application/json',response_json_schema=SCHEMA)
        self.assertIsNotNone(config.response_json_schema)
        with genai.Client(enterprise=True,project='offline-test-project',location='global',credentials=AnonymousCredentials()):
            pass

if __name__=='__main__':unittest.main()
