# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# repository for reading pending dependabot alerts and writing alert reviews
import json
from datetime import datetime, timedelta, timezone
import psycopg
from psycopg.rows import dict_row

from logging_util import console_logging
from schemas import AlertGroup, AlertRecord, AlertReviewWrite, \
    StoredRiskAssessment

logger = console_logging("Postgres review repository")


class PostgresReviewRepository:
    def __init__(
        self,
        *,
        dsn: str | None = None,
        db_host: str | None = None,
        db_port: int | None = None,
        database: str | None = None,
        postgres_user: str | None = None,
        postgres_password: str | None = None,
    ):
        self.dsn = dsn
        self.db_host = db_host
        self.db_port = db_port
        self.database = database
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.conn = None
        self.connect()

    def postgres_connection(
        self,
        *,
        dsn: str | None = None,
        db_host: str | None = None,
        db_port: int | None = None,
        database: str | None = None,
        postgres_user: str | None = None,
        postgres_password: str | None = None,
    ):
        if dsn:
            logger.info("Connecting to Postgres using DSN")
            return psycopg.connect(dsn, autocommit=True)

        logger.info(
            "Connecting to Postgres using parameters host=%s port=%s dbname=%s user=%s",  # noqa: E501
            db_host,
            db_port,
            database,
            postgres_user,
        )

        params = {
            "host": db_host,
            "dbname": database,
            "port": db_port,
            "user": postgres_user,
            "password": postgres_password,
        }

        return psycopg.connect(**params, autocommit=True)

    def connect(self) -> None:
        if self.conn is None or self.conn.closed:
            self.conn = self.postgres_connection(
                dsn=self.dsn,
                db_host=self.db_host,
                db_port=self.db_port,
                database=self.database,
                postgres_user=self.postgres_user,
                postgres_password=self.postgres_password,
            )

            with self.conn.cursor() as cur:
                cur.execute("select current_database(), current_user, current_schema()")  # noqa: E501
                db_name, db_user, db_schema = cur.fetchone()
                logger.info(
                    "Postgres connection established database=%s user=%s schema=%s",  # noqa: E501
                    db_name,
                    db_user,
                    db_schema,
                )

    def close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            logger.info("Closing Postgres connection")
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def fetch_alert_groups_needing_review(
        self,
        *,
        limit: int = 25,
    ) -> list[AlertGroup]:
        self.connect()

        sql = """
            SELECT
                repo_full_name,
                package_name,
                ecosystem,
                MIN(severity)                       AS severity,
                MIN(summary)                        AS summary,
                MIN(description)                    AS description,
                MIN(cve_id)                         AS cve_id,
                MIN(ghsa_id)                        AS ghsa_id,
                MIN(vulnerable_version_range)       AS vulnerable_version_range,
                MIN(first_patched_version)          AS first_patched_version,
                MIN(review_group_key)               AS review_group_key,
                MIN(review_reason)                  AS review_reason,
                array_agg(manifest_path ORDER BY alert_number ASC) AS manifest_paths,
                array_agg(alert_id      ORDER BY alert_number ASC) AS alert_ids,
                array_agg(alert_number  ORDER BY alert_number ASC) AS alert_numbers
            FROM dependabot_alerts
            WHERE github_state = 'open'
            AND needs_review = TRUE
            GROUP BY repo_full_name, package_name, ecosystem
            ORDER BY MIN(alert_number) ASC
            LIMIT %s
        """

        logger.info("Fetching alert groups needing review limit=%s", limit)

        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, [limit])
            rows = cur.fetchall()

        repos = sorted({row["repo_full_name"] for row in rows})
        logger.info(
            "Fetched %s alert groups across %s repos: %s",
            len(rows),
            len(repos),
            ", ".join(repos),
        )

        return [AlertGroup.model_validate(row) for row in rows]

    def fetch_alerts_needing_slack_notification(
        self,
        *,
        reminder_interval_hours: int = 24,
    ) -> list[AlertRecord]:
        self.connect()

        cutoff = datetime.\
            now(tz=timezone.utc) - timedelta(hours=reminder_interval_hours)

        sql = """
            SELECT *
            FROM dependabot_alerts
            WHERE github_state = 'open'
            AND needs_review = FALSE
            AND (
                slack_notified_at IS NULL
                OR slack_message_ts < %(cutoff)s
            )
            ORDER BY alert_number ASC
        """

        logger.info(
            "Fetching alerts needing Slack notification reminder_interval_hours=%s",  # noqa: E501
            reminder_interval_hours,
        )

        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, {"cutoff": cutoff})
            rows = cur.fetchall()
            logger.info("Fetched %s alerts needing Slack notification",
                        len(rows))

        return [AlertRecord.model_validate(row) for row in rows]

    def fetch_latest_assessment(
        self,
        alert_id: str,
    ) -> StoredRiskAssessment | None:
        self.connect()

        sql = """
            SELECT
                alert_id,
                recommendation,
                priority                AS severity,
                confidence,
                risksummary             AS risk_summary,
                reasoning,
                current_version,
                suggested_version,
                cve_summary,
                usage_in_codebase,
                breaking_change_risk,
                breaking_change_rationale,
                suggested_pr_description,
                assessment_json
            FROM dependabot_alert_reviews
            WHERE alert_id = %s
            ORDER BY reviewed_at DESC
            LIMIT 1
        """

        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, (alert_id,))
            row = cur.fetchone()

        if row is None:
            logger.warning("No assessment found for alert_id=%s", alert_id)
            return None

        assessment_json = row.get("assessment_json") or {}

        return StoredRiskAssessment(
            alert_id=row["alert_id"],
            manifest_path=assessment_json.get("manifest_path", ""),
            package=assessment_json.get("package", ""),
            ecosystem=assessment_json.get("ecosystem", ""),
            severity=assessment_json.get("severity", row["severity"]),
            current_version=row["current_version"],
            suggested_version=row["suggested_version"],
            cve_summary=row["cve_summary"] or "",
            usage_in_codebase=row["usage_in_codebase"] or "",
            breaking_change_risk=row["breaking_change_risk"] or "low",
            breaking_change_rationale=row["breaking_change_rationale"] or "",
            recommendation=row["recommendation"],
            suggested_pr_description=row["suggested_pr_description"] or "",
            priority=row["severity"],
            confidence=row["confidence"],
            risk_summary=row["risk_summary"] or "",
            reasoning=row["reasoning"] or "",
        )

    def mark_alert_slack_notified(
        self,
        *,
        alert_id: str,
        is_reminder: bool,
        notified_at: datetime,
    ) -> None:
        self.connect()

        if is_reminder:
            sql = """
                UPDATE dependabot_alerts
                SET
                    slack_message_ts = %(notified_at)s,
                    reminder_count   = COALESCE(reminder_count, 0) + 1,
                    updated_at       = NOW()
                WHERE alert_id = %(alert_id)s
            """
        else:
            sql = """
                UPDATE dependabot_alerts
                SET
                    slack_notified_at = %(notified_at)s,
                    slack_message_ts  = %(notified_at)s,
                    reminder_count    = 0,
                    updated_at        = NOW()
                WHERE alert_id = %(alert_id)s
            """

        payload = {"alert_id": alert_id, "notified_at": notified_at}

        with self.conn.cursor() as cur:
            cur.execute(sql, payload)
            logger.info(
                "Marked alert Slack notified rowcount=%s alert_id=%s is_reminder=%s",  # noqa: E501
                cur.rowcount,
                alert_id,
                is_reminder,
            )

    def insert_review(self, review: AlertReviewWrite) -> None:
        self.connect()

        sql = """
            INSERT INTO dependabot_alert_reviews (
                alert_id,
                repo_full_name,
                review_group_key,
                review_reason,
                model_name,
                prompt_version,
                recommendation,
                priority,
                confidence,
                risksummary,
                reasoning,
                current_version,
                suggested_version,
                cve_summary,
                usage_in_codebase,
                breaking_change_risk,
                breaking_change_rationale,
                suggested_pr_description,
                research_json,
                assessment_json
            )
            VALUES (
                %(alert_id)s,
                %(repo_full_name)s,
                %(review_group_key)s,
                %(review_reason)s,
                %(model_name)s,
                %(prompt_version)s,
                %(recommendation)s,
                %(priority)s,
                %(confidence)s,
                %(risksummary)s,
                %(reasoning)s,
                %(current_version)s,
                %(suggested_version)s,
                %(cve_summary)s,
                %(usage_in_codebase)s,
                %(breaking_change_risk)s,
                %(breaking_change_rationale)s,
                %(suggested_pr_description)s,
                %(research_json)s::jsonb,
                %(assessment_json)s::jsonb
            )
        """

        payload = review.model_dump(mode="python")
        payload["research_json"] = json.dumps(payload["research_json"])
        payload["assessment_json"] = json.dumps(payload["assessment_json"])

        with self.conn.cursor() as cur:
            cur.execute(sql, payload)
            logger.info(
                "Inserted review rowcount=%s alert_id=%s",
                cur.rowcount,
                review.alert_id,
            )

    def mark_alert_reviewed(
        self,
        *,
        alert_id: str,
        latest_research_json: dict,
    ) -> None:
        self.connect()

        sql = """
            UPDATE dependabot_alerts
            SET
                needs_review         = FALSE,
                last_researched_at   = NOW(),
                latest_research_json = %(latest_research_json)s::jsonb,
                updated_at           = NOW()
            WHERE alert_id = %(alert_id)s
        """

        payload = {
            "alert_id": alert_id,
            "latest_research_json": json.dumps(latest_research_json),
        }

        with self.conn.cursor() as cur:
            cur.execute(sql, payload)
            logger.info(
                "Updated alert rowcount=%s alert_id=%s",
                cur.rowcount,
                alert_id,
            )

    def save_review_result(
        self,
        *,
        review: AlertReviewWrite,
        latest_research_json: dict,
    ) -> None:
        self.connect()

        logger.info("Saving review result for alert_id=%s", review.alert_id)

        with self.conn.transaction():
            self.insert_review(review)
            self.mark_alert_reviewed(
                alert_id=review.alert_id,
                latest_research_json=latest_research_json,
            )

        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT alert_id, needs_review, last_researched_at
                FROM dependabot_alerts
                WHERE alert_id = %s
                """,
                (review.alert_id,),
            )
            row = cur.fetchone()
            logger.info("Post-write alert state for %s: %s", review.alert_id, row)  # noqa: E501
