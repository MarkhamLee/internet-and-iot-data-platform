# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Postgres client for synching and upserting of GitHub dependabot
# back-end data for the dependabot research agent.
import psycopg
from datetime import datetime, timezone
from psycopg import DatabaseError
from psycopg.types.json import Jsonb
from typing import Any
from logging_util import console_logging

logger = console_logging('Data_synching')


def postgres_connection(
    db_host: str,
    db_port: int,
    database: str,
    postgres_user: str,
    postgres_password: str,
):
    params = {
        "host": db_host,
        "dbname": database,
        "port": db_port,
        "user": postgres_user,
        "password": postgres_password,
    }

    try:
        conn = psycopg.connect(**params)
        logger.info("Connection to Postgres successful")
        return conn

    except DatabaseError as error:
        logger.exception("Postgres connection failed: %s", error)
        raise


def sync_open_alerts(
    *,
    conn: psycopg.Connection,
    repo_full_name: str,
    prepared_alerts: list[dict[str, Any]],
) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    current_open_ids = [item["alert_id"] for item in prepared_alerts]

    upsert_sql = """
    INSERT INTO dependabot_alerts (
        alert_id,
        repo_owner,
        repo_name,
        repo_full_name,
        repo_html_url,
        repo_api_url,
        alert_number,
        github_state,
        package_name,
        ecosystem,
        manifest_path,
        scope,
        relationship,
        severity,
        summary,
        description,
        cve_id,
        ghsa_id,
        vulnerable_version_range,
        first_patched_version,
        alert_html_url,
        source_fingerprint,
        review_group_key,
        needs_review,
        review_reason,
        first_seen_at,
        last_seen_open_at,
        last_state_change_at,
        last_synced_at,
        raw_alert_json,
        updated_at
    )
    VALUES (
        %(alert_id)s,
        %(repo_owner)s,
        %(repo_name)s,
        %(repo_full_name)s,
        %(repo_html_url)s,
        %(repo_api_url)s,
        %(alert_number)s,
        'open',
        %(package_name)s,
        %(ecosystem)s,
        %(manifest_path)s,
        %(scope)s,
        %(relationship)s,
        %(severity)s,
        %(summary)s,
        %(description)s,
        %(cve_id)s,
        %(ghsa_id)s,
        %(vulnerable_version_range)s,
        %(first_patched_version)s,
        %(alert_html_url)s,
        %(source_fingerprint)s,
        %(review_group_key)s,
        TRUE,
        'new_alert',
        %(now)s,
        %(now)s,
        %(now)s,
        %(now)s,
        %(raw_alert_json)s,
        %(now)s
    )
    ON CONFLICT (alert_id) DO UPDATE
    SET
        repo_owner = EXCLUDED.repo_owner,
        repo_name = EXCLUDED.repo_name,
        repo_full_name = EXCLUDED.repo_full_name,
        repo_html_url = EXCLUDED.repo_html_url,
        repo_api_url = EXCLUDED.repo_api_url,
        alert_number = EXCLUDED.alert_number,
        github_state = 'open',
        package_name = EXCLUDED.package_name,
        ecosystem = EXCLUDED.ecosystem,
        manifest_path = EXCLUDED.manifest_path,
        scope = EXCLUDED.scope,
        relationship = EXCLUDED.relationship,
        severity = EXCLUDED.severity,
        summary = EXCLUDED.summary,
        description = EXCLUDED.description,
        cve_id = EXCLUDED.cve_id,
        ghsa_id = EXCLUDED.ghsa_id,
        vulnerable_version_range = EXCLUDED.vulnerable_version_range,
        first_patched_version = EXCLUDED.first_patched_version,
        alert_html_url = EXCLUDED.alert_html_url,
        review_group_key = EXCLUDED.review_group_key,
        raw_alert_json = EXCLUDED.raw_alert_json,
        last_seen_open_at = EXCLUDED.last_seen_open_at,
        last_synced_at = EXCLUDED.last_synced_at,
        updated_at = EXCLUDED.updated_at,
        resolved_at = NULL,
        needs_review = CASE
            WHEN dependabot_alerts.source_fingerprint IS DISTINCT FROM EXCLUDED.source_fingerprint THEN TRUE
            WHEN dependabot_alerts.github_state IS DISTINCT FROM 'open' THEN TRUE
            ELSE dependabot_alerts.needs_review
        END,
        review_reason = CASE
            WHEN dependabot_alerts.source_fingerprint IS DISTINCT FROM EXCLUDED.source_fingerprint THEN 'alert_changed'
            WHEN dependabot_alerts.github_state IS DISTINCT FROM 'open' THEN 'reopened_or_seen_open_again'
            ELSE dependabot_alerts.review_reason
        END,
        last_state_change_at = CASE
            WHEN dependabot_alerts.github_state IS DISTINCT FROM 'open' THEN EXCLUDED.last_state_change_at
            WHEN dependabot_alerts.source_fingerprint IS DISTINCT FROM EXCLUDED.source_fingerprint THEN EXCLUDED.last_state_change_at
            ELSE dependabot_alerts.last_state_change_at
        END,
        source_fingerprint = EXCLUDED.source_fingerprint
    """

    close_missing_sql = """
    UPDATE dependabot_alerts
    SET
        github_state = 'closed_pending_reason',
        resolved_at = %(now)s,
        last_state_change_at = %(now)s,
        last_synced_at = %(now)s,
        updated_at = %(now)s
    WHERE repo_full_name = %(repo_full_name)s
      AND github_state = 'open'
      AND NOT (alert_id = ANY(%(current_open_ids)s))
    """

    close_all_sql = """
    UPDATE dependabot_alerts
    SET
        github_state = 'closed_pending_reason',
        resolved_at = %(now)s,
        last_state_change_at = %(now)s,
        last_synced_at = %(now)s,
        updated_at = %(now)s
    WHERE repo_full_name = %(repo_full_name)s
      AND github_state = 'open'
    """

    with conn.transaction():
        with conn.cursor() as cur:
            for item in prepared_alerts:
                payload = {
                    **item,
                    "now": now,
                    "raw_alert_json": Jsonb(item["raw_alert_json"]),
                }
                cur.execute(upsert_sql, payload)

            if current_open_ids:
                cur.execute(
                    close_missing_sql,
                    {
                        "repo_full_name": repo_full_name,
                        "current_open_ids": current_open_ids,
                        "now": now,
                    },
                )
                closed_count = cur.rowcount
            else:
                cur.execute(
                    close_all_sql,
                    {
                        "repo_full_name": repo_full_name,
                        "now": now,
                    },
                )
                closed_count = cur.rowcount

    return {
        "received_open_alerts": len(prepared_alerts),
        "closed_missing_alerts": closed_count,
    }
