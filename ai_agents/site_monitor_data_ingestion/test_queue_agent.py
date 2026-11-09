# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# PostgreSQL repository for the site monitor research queue
# Isolated tests: services mocked; no PostgreSQL, HTTP, Ollama, or Slack access

import sys
import types
import unittest
from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock, patch

for name in ('platform_utils', 'platform_utils.platform_logger', 'config', 'content_extractor',
             'hash_helper', 'page_fetcher', 'ingestion_instrumentation_store'):
    sys.modules[name] = types.ModuleType(name)
sys.modules['platform_utils.platform_logger'].configure_logger = lambda name: MagicMock()
sys.modules['config'].AppConfig = object
sys.modules['config'].WatchTarget = object
sys.modules['content_extractor'].extract_review_payload = MagicMock(return_value={})
sys.modules['hash_helper'].compute_content_hash = MagicMock(return_value='hash')
sys.modules['page_fetcher'].fetch_page = MagicMock()
sys.modules['ingestion_instrumentation_store'].IngestionInstrumentationStore = object
schemas = types.ModuleType('schemas')
for name in ('ResearchQueueItem', 'PageReviewResult', 'TrackedPageState'):
    setattr(schemas, name, types.SimpleNamespace)
sys.modules['schemas'] = schemas
try:
    import psycopg
except ImportError:
    driver = types.ModuleType('psycopg')
    driver.connect = MagicMock()
    sys.modules['psycopg'] = driver
    for name in ('psycopg.rows', 'psycopg.types', 'psycopg.types.json'):
        sys.modules[name] = types.ModuleType(name)
    sys.modules['psycopg.rows'].dict_row = object()
    sys.modules['psycopg.types.json'].Jsonb = lambda value: value
import research_queue_store as queue
import state_store as state
import ingestion_pipeline as pipeline

NOW = datetime.now(UTC)
def connection():
    conn = MagicMock()
    conn.__enter__.return_value = conn
    cur = conn.cursor.return_value.__enter__.return_value
    return conn, cur

def params():
    return dict(page_key='watch', url='https://example.test', request_reason='content_changed',
                content_hash='hash', final_url=None, http_etag=None, http_last_modified=None,
                pending_reconfirmation=False, payload={})

def previous(**kwargs):
    values = dict(current_status='undesired', last_llm_reviewed_hash='hash',
                  last_content_hash='hash', last_research_completed_at=NOW - timedelta(days=2),
                  last_checked_at=NOW, last_http_etag='etag', last_http_last_modified=None)
    values.update(kwargs)
    return types.SimpleNamespace(**values)

class EnqueueTests(unittest.TestCase):
    def test_reuses_active_and_locks(self):
        conn, cur = connection()
        cur.fetchone.return_value = (7,)
        self.assertEqual(queue.ResearchQueueStore('dsn').enqueue_research(**params(), conn=conn), (7, False))
        sql = cur.execute.call_args.args[0]
        self.assertIn("status IN ('pending', 'in_progress')", sql)
        self.assertIn('FOR UPDATE', sql)
        self.assertEqual(cur.execute.call_count, 1)

    def test_new_insert(self):
        conn, cur = connection()
        cur.fetchone.side_effect = [None, (8,)]
        self.assertEqual(queue.ResearchQueueStore('dsn').enqueue_research(**params(), conn=conn), (8, True))
        self.assertIn('ON CONFLICT (page_key, content_hash)', cur.execute.call_args.args[0])

    def test_conflict_then_reuse(self):
        conn, cur = connection()
        cur.fetchone.side_effect = [None, None, (9,)]
        self.assertEqual(queue.ResearchQueueStore('dsn').enqueue_research(**params(), conn=conn), (9, False))

    def test_completed_conflict_then_new_insert(self):
        conn, cur = connection()
        cur.fetchone.side_effect = [None, None, None, (10,)]
        self.assertEqual(queue.ResearchQueueStore('dsn').enqueue_research(**params(), conn=conn), (10, True))

    def test_repeated_churn_raises(self):
        conn, cur = connection()
        cur.fetchone.return_value = None
        with self.assertRaises(RuntimeError):
            queue.ResearchQueueStore('dsn').enqueue_research(**params(), conn=conn)

    def test_missing_hash_rejected(self):
        args = params(); args['content_hash'] = None
        with self.assertRaises(ValueError):
            queue.ResearchQueueStore('dsn').enqueue_research(**args)

class StateTests(unittest.TestCase):
    def test_refresh_uses_review_clock(self):
        self.assertEqual(state.should_enqueue_research(previous(), 'hash', NOW, 24), (True, 'forced_refresh'))

    def test_recent_review_no_refresh(self):
        self.assertEqual(state.should_enqueue_research(
            previous(last_research_completed_at=NOW), 'hash', NOW, 24), (False, 'content_unchanged'))

    def test_never_reviewed(self):
        self.assertEqual(state.should_enqueue_research(
            previous(last_research_completed_at=None), 'hash', NOW, 24), (True, 'never_reviewed'))

    def test_mark_pending_uses_supplied_connection(self):
        conn, cur = connection(); cur.rowcount = 1
        with patch.object(state.psycopg, 'connect') as connect:
            state.StateStore('dsn').mark_research_pending(page_key='watch', url='url', now=NOW,
                content_hash='hash', queue_id=7, pending_reconfirmation=False,
                final_url=None, http_etag=None, http_last_modified=None, conn=conn)
        connect.assert_not_called()
        self.assertEqual(cur.execute.call_count, 2)

class PipelineTests(unittest.TestCase):
    def setup_case(self, prev):
        deps = types.SimpleNamespace(state_store=MagicMock(), queue_store=MagicMock(),
                                     instrumentation_store=MagicMock(), logger=MagicMock())
        deps.state_store.get_current_state.return_value = prev
        deps.queue_store.enqueue_research.return_value = (8, True)
        target = types.SimpleNamespace(page_key='watch', url='https://example.test', enabled=True)
        app = types.SimpleNamespace(postgres_dsn='dsn', force_research_after_hours=24)
        return app, deps, target

    def fetched(self, code):
        return types.SimpleNamespace(status_code=code, final_url='https://example.test',
                                     etag='etag', last_modified=None)

    def test_queue_and_state_share_transaction(self):
        app, deps, target = self.setup_case(None)
        conn, cur = connection()
        with patch.object(pipeline, 'fetch_page', return_value=self.fetched(200)), \
             patch.object(pipeline, 'build_research_queue_payload', return_value={}), \
             patch.object(pipeline.psycopg, 'connect', return_value=conn):
            outcome = pipeline.process_target(app=app, target=target, deps=deps, run_id=1)
        self.assertEqual(outcome, 'queued')
        self.assertIs(deps.queue_store.enqueue_research.call_args.kwargs['conn'], conn)
        self.assertIs(deps.state_store.mark_research_pending.call_args.kwargs['conn'], conn)

    def test_state_failure_escapes_outer_transaction(self):
        app, deps, target = self.setup_case(None)
        deps.state_store.mark_research_pending.side_effect = RuntimeError('state failure')
        conn, cur = connection()
        with patch.object(pipeline, 'fetch_page', return_value=self.fetched(200)), \
             patch.object(pipeline, 'build_research_queue_payload', return_value={}), \
             patch.object(pipeline.psycopg, 'connect', return_value=conn):
            self.assertEqual(pipeline.process_target(app=app, target=target, deps=deps, run_id=1), 'failed')
        self.assertIs(conn.transaction.return_value.__exit__.call_args.args[0], RuntimeError)

    def test_304_due_refresh_fetches_body(self):
        app, deps, target = self.setup_case(previous())
        conn, cur = connection()
        with patch.object(pipeline, 'fetch_page', side_effect=[self.fetched(304), self.fetched(200)]) as fetch, \
             patch.object(pipeline, 'build_research_queue_payload', return_value={}), \
             patch.object(pipeline.psycopg, 'connect', return_value=conn):
            self.assertEqual(pipeline.process_target(app=app, target=target, deps=deps, run_id=1), 'queued')
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(fetch.call_args.kwargs, {})

    def test_304_recent_review_stays_unchanged(self):
        app, deps, target = self.setup_case(previous(last_research_completed_at=NOW))
        with patch.object(pipeline, 'fetch_page', return_value=self.fetched(304)) as fetch:
            self.assertEqual(pipeline.process_target(app=app, target=target, deps=deps, run_id=1), 'unchanged')
        self.assertEqual(fetch.call_count, 1)
        deps.queue_store.enqueue_research.assert_not_called()

if __name__ == '__main__':
    unittest.main()
