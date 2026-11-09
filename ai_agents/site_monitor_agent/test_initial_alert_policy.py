# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# PostgreSQL repository for the site monitor research queue

import sys
import types
import unittest
from datetime import datetime, UTC
from unittest.mock import MagicMock, patch

for name in ('platform_utils', 'platform_utils.platform_logger', 'platform_utils.alert_utils',
             'agent_library', 'agent_library.qwen_client', 'config'):
    sys.modules[name] = types.ModuleType(name)
sys.modules['platform_utils.platform_logger'].configure_logger = lambda name: MagicMock()
sys.modules['platform_utils.alert_utils'].send_slack_webhook_block = MagicMock(return_value=200)
sys.modules['agent_library.qwen_client'].QwenClient = object
sys.modules['config'].AppConfig = object
try:
    import psycopg
except ImportError:
    driver = types.ModuleType('psycopg')
    driver.connect = MagicMock()
    driver.errors = types.SimpleNamespace(UniqueViolation=type('UniqueViolation', (Exception,), {}))
    sys.modules['psycopg'] = driver
    rows = types.ModuleType('psycopg.rows'); rows.dict_row = object()
    sys.modules['psycopg.rows'] = rows

from schemas import decide_initial_alert, PageAnalysisResponse, PageAnalysisWrite, ResearchQueueItem
import postgres_queue_repository as repository
import research_pipeline as pipeline
from slack_messaging import build_alert_blocks

NOW = datetime.now(UTC)
def item(flag=True):
    return ResearchQueueItem(id=1, page_key='watch', url='https://example.test', requested_at=NOW,
        claimed_at=NOW, status='in_progress', request_reason='forced_refresh', content_hash='hash',
        attempt_count=1, payload={'target_metadata': {'send_missed_it_message': flag}})
def response(status='desired', action='alert'):
    return PageAnalysisResponse(desired_state_found=status == 'desired', confidence='high',
        summary='Evidence summary', reasoning='Evidence', recommended_action=action,
        result_page_status=status, result_event_type='model_invented_event')
def result(status='desired'):
    return PageAnalysisWrite(**response(status).model_dump(), queue_id=1, page_key='watch',
                             url='https://example.test', model_name='test')

class PolicyTests(unittest.TestCase):
    def test_all_transitions_both_flags(self):
        states = ['desired', 'undesired', 'unknown']
        for prev in states:
            for curr in states:
                for flag in [True, False]:
                    with self.subTest(previous=prev, current=curr, flag=flag):
                        decision = decide_initial_alert(prev, curr, send_missed_it_message=flag)
                        expected = (curr == 'desired' and prev != 'desired') or (
                            prev == 'desired' and curr == 'undesired' and flag)
                        self.assertEqual(decision.should_alert, expected)
                        self.assertEqual(decision.state_changed, prev != curr)
                        self.assertEqual(decision.suppression_reason is None, expected)

    def test_malformed_flag_rejected(self):
        with self.assertRaises(ValueError):
            decide_initial_alert('desired', 'undesired', send_missed_it_message='false')

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            decide_initial_alert('success', 'desired', send_missed_it_message=True)

class RepositoryTests(unittest.TestCase):
    def run_completion(self, previous, current, flag=True):
        conn = MagicMock(); conn.__enter__.return_value = conn
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [('watch', 'hash', 'in_progress', NOW, 1), (previous,)]
        cur.rowcount = 1
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            completion = repository.PostgresQueueRepository('dsn').complete_research(
                item=item(flag), result=result(current), now=NOW)
        return completion, conn, cur

    def test_state_locked_before_writes_and_event_is_application_owned(self):
        completion, conn, cur = self.run_completion('undesired', 'desired')
        self.assertTrue(completion.should_alert)
        calls = cur.execute.call_args_list
        self.assertIn('FOR UPDATE', calls[1].args[0])
        self.assertIn('page_watch_current', calls[1].args[0])
        self.assertEqual(calls[3].args[1]['event_type'], 'became_desired')
        self.assertEqual(len(calls), 4)
        conn.transaction.assert_called_once()

    def test_second_same_state_completion_suppresses(self):
        first, _, _ = self.run_completion('undesired', 'desired')
        second, _, _ = self.run_completion('desired', 'desired')
        self.assertTrue(first.should_alert)
        self.assertFalse(second.should_alert)

    def test_non_boolean_missed_it_is_fail_closed(self):
        completion, _, _ = self.run_completion('desired', 'undesired', 'false')
        self.assertFalse(completion.should_alert)

    def test_missing_state_raises_inside_transaction(self):
        conn = MagicMock(); conn.__enter__.return_value = conn
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [('watch', 'hash', 'in_progress', NOW, 1), None]
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            with self.assertRaises(RuntimeError):
                repository.PostgresQueueRepository('dsn').complete_research(
                    item=item(), result=result(), now=NOW)
        self.assertIs(conn.transaction.return_value.__exit__.call_args.args[0], RuntimeError)
        self.assertEqual(cur.execute.call_count, 2)

    def test_commit_exception_does_not_return_decision(self):
        conn = MagicMock(); conn.__enter__.return_value = conn
        conn.__exit__.side_effect = RuntimeError('commit failed')
        cur = conn.cursor.return_value.__enter__.return_value
        cur.fetchone.side_effect = [('watch', 'hash', 'in_progress', NOW, 1), ('undesired',)]
        cur.rowcount = 1
        with patch.object(repository.psycopg, 'connect', return_value=conn):
            with self.assertRaisesRegex(RuntimeError, 'commit failed'):
                repository.PostgresQueueRepository('dsn').complete_research(
                    item=item(), result=result(), now=NOW)

class PipelineTests(unittest.TestCase):
    def setup_run(self, prev, curr, flag=True):
        repo = MagicMock(); repo.claim_item.return_value = item(flag)
        repo.complete_research.return_value = decide_initial_alert(prev, curr, send_missed_it_message=flag)
        client = MagicMock(model='test'); client.generate_structured_response.return_value = response(curr)
        return repo, client

    def run_item(self, repo, client, send):
        metrics = {}
        with patch.object(pipeline, 'PostgresQueueRepository', return_value=repo), \
             patch.object(pipeline, 'send_slack_webhook_block', send):
            outcome, write = pipeline.process_queue_item(item=item(),
                app=types.SimpleNamespace(postgres_dsn='dsn', slack_webhook_url='test'),
                client=client, metrics=metrics)
        return outcome, write, metrics

    def test_model_alert_cannot_override_same_state(self):
        repo, client = self.setup_run('undesired', 'undesired')
        send = MagicMock(return_value=200)
        outcome, write, metrics = self.run_item(repo, client, send)
        self.assertEqual(outcome, 'no_action'); send.assert_not_called()
        self.assertTrue(metrics['research_committed']); self.assertTrue(metrics['alert_suppressed'])
        self.assertEqual(write.result_event_type, 'state_unchanged')

    def test_transition_sends_application_event(self):
        repo, client = self.setup_run('undesired', 'desired')
        send = MagicMock(return_value=200)
        outcome, write, metrics = self.run_item(repo, client, send)
        self.assertEqual(outcome, 'alerted')
        self.assertIn('Desired state reached', send.call_args.args[1]['text'])
        self.assertEqual(write.result_event_type, 'became_desired')

    def test_missed_it_notification(self):
        repo, client = self.setup_run('desired', 'undesired')
        send = MagicMock(return_value=200)
        outcome, write, _ = self.run_item(repo, client, send)
        self.assertEqual(outcome, 'alerted')
        self.assertIn('Desired state no longer met', send.call_args.args[1]['text'])

    def test_persistence_failure_never_sends(self):
        repo, client = self.setup_run('undesired', 'desired')
        repo.complete_research.side_effect = RuntimeError('write failed')
        send = MagicMock()
        outcome, _, _ = self.run_item(repo, client, send)
        self.assertEqual(outcome, 'failed'); send.assert_not_called()

    def test_slack_failure_does_not_fail_research(self):
        repo, client = self.setup_run('undesired', 'desired')
        outcome, _, metrics = self.run_item(repo, client, MagicMock(return_value=500))
        self.assertEqual(outcome, 'notification_failed')
        self.assertTrue(metrics['research_committed']); repo.fail_item.assert_not_called()

class SlackTests(unittest.TestCase):
    def test_application_label_overrides_model_action(self):
        decision = decide_initial_alert('desired', 'undesired', send_missed_it_message=True)
        write = result('undesired')
        write.recommended_action = 'no_action'
        payload = build_alert_blocks(write, NOW, completion=decision)
        self.assertIn('Desired state no longer met', payload['text'])
        self.assertIn('became_undesired', str(payload['blocks']))
        self.assertNotIn('model_invented_event', str(payload))

if __name__ == '__main__':
    unittest.main()
