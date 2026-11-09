# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# PostgreSQL repository for the site monitor research queue

import sys
import types
import unittest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

for name in ('platform_utils',
             'platform_utils.platform_logger',
             'platform_utils.alert_utils',
             'agent_library',
             'agent_library.qwen_client',
             'config',
             'slack_messaging'):
    sys.modules[name] = types.ModuleType(name)
sys.modules['platform_utils.platform_logger'].configure_logger = lambda name: MagicMock()
sys.modules['platform_utils.alert_utils'].send_slack_webhook_block = MagicMock(return_value=200)
sys.modules['agent_library.qwen_client'].QwenClient = object
sys.modules['config'].AppConfig = object
sys.modules['slack_messaging'].build_alert_blocks = MagicMock(return_value={})

try:
    import psycopg  # noqa: F401
except ImportError:
    driver = types.ModuleType('psycopg')

    class UniqueViolation(Exception):
        def __init__(self, constraint):
            self.diag = types.SimpleNamespace(constraint_name=constraint)
    driver.errors = types.SimpleNamespace(UniqueViolation=UniqueViolation)
    driver.connect = MagicMock()
    sys.modules['psycopg'] = driver
    rows = types.ModuleType('psycopg.rows')
    rows.dict_row = object()
    sys.modules['psycopg.rows'] = rows
import postgres_queue_repository as repository
import research_pipeline as pipeline
from schemas import ResearchQueueItem, PageAnalysisResponse

NOW = datetime.now(UTC)
def row():
    return dict(id=1, page_key='watch', url='https://example.test', requested_at=NOW,
                claimed_at=NOW, status='in_progress', request_reason='content_changed',
                content_hash='abc', attempt_count=2, max_attempts=5, payload={})

class QueueTests(unittest.TestCase):
    def connection(self):
        conn = MagicMock()
        conn.__enter__.return_value = conn
        return conn, conn.cursor.return_value.__enter__.return_value

    def test_claim_returns_fresh_item(self):
        conn, cur = self.connection()
        cur.fetchone.return_value = row()
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            item = repository.PostgresQueueRepository('dsn').claim_item(1, NOW)
        self.assertEqual(item.attempt_count, 2)
        self.assertEqual(item.claimed_at, NOW)
        self.assertIn('SKIP LOCKED', cur.execute.call_args.args[0])

    def test_no_claim_is_skip(self):
        conn, cur = self.connection()
        cur.fetchone.return_value = None
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            self.assertIsNone(repository.PostgresQueueRepository('dsn').claim_item(1, NOW))

    def test_failure_has_ownership_guard_and_backoff(self):
        conn, cur = self.connection()
        cur.rowcount = 1
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            ok = repository.PostgresQueueRepository('dsn').fail_item(
                item=ResearchQueueItem(**row()), now=NOW, error_message='error')
        self.assertTrue(ok)
        sql, params = cur.execute.call_args.args
        self.assertIn('claimed_at = %(claimed_at)s', sql)
        self.assertIn('attempt_count = %(attempt_count)s', sql)
        self.assertEqual(params['delay'], 900)

    def test_stale_failure_not_recorded(self):
        conn, cur = self.connection()
        cur.rowcount = 0
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            self.assertFalse(repository.PostgresQueueRepository('dsn').fail_item(
                item=ResearchQueueItem(**row()), now=NOW, error_message='old worker'))

    def test_fetch_excludes_failed_with_active_equivalent(self):
        conn, cur = self.connection()
        cur.fetchall.return_value = []
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            repository.PostgresQueueRepository('dsn').fetch_pending_items()
        sql = cur.execute.call_args.args[0]
        self.assertIn('NOT EXISTS', sql)
        self.assertIn("active.status IN ('pending', 'in_progress')", sql)

class PipelineTests(unittest.TestCase):
    def test_skips_without_inference_or_failure(self):
        repo = MagicMock()
        repo.claim_item.return_value = None
        client = MagicMock()
        metrics = {}
        with patch.object(pipeline, 'PostgresQueueRepository', return_value=repo):
            outcome, _ = pipeline.process_queue_item(item=ResearchQueueItem(**row()),
                app=types.SimpleNamespace(postgres_dsn='dsn'), client=client, metrics=metrics)
        self.assertEqual(outcome, 'skipped')
        client.generate_structured_response.assert_not_called()
        repo.fail_item.assert_not_called()

    def test_fresh_claim_passed_to_completion(self):
        fresh = ResearchQueueItem(**row())
        repo = MagicMock()
        repo.claim_item.return_value = fresh
        client = MagicMock(model='test')
        client.generate_structured_response.return_value = PageAnalysisResponse(
            desired_state_found=False, confidence='high', summary='No match', reasoning='Evidence',
            recommended_action='monitor', result_page_status='undesired', result_event_type=None)
        metrics = {}
        with patch.object(pipeline, 'PostgresQueueRepository', return_value=repo):
            outcome, _ = pipeline.process_queue_item(item=fresh,
                app=types.SimpleNamespace(postgres_dsn='dsn'), client=client, metrics=metrics)
        self.assertEqual(outcome, 'no_action')
        self.assertIs(repo.complete_research.call_args.kwargs['item'], fresh)
        self.assertTrue(metrics['research_committed'])


if __name__ == '__main__':
    unittest.main()
