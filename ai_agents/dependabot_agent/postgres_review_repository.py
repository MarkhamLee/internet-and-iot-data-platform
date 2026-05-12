# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# repository for reading pending dependabot alerts and writing alert reviews
import json
import psycopg
from psycopg.rows import dict_row
from schemas import AlertRecord, AlertReviewWrite


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
            return psycopg.connect(dsn)

        params = {
            "host": db_host,
            "dbname": database,
            "port": db_port,
            "user": postgres_user,
            "password": postgres_password,
        }

        return psycopg.connect(**params)

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

    def close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def fetch_alerts_needing_review(
        self,
        *,
        repo_full_name: str | None = None,
        limit: int = 25,
    ) -> list[AlertRecord]:
        self.connect()

        where_clauses = [
            "github_state = 'open'",
            "needs_review = TRUE",
        ]
        params = []

        if repo_full_name:
            where_clauses.append("repo_full_name = %s")
            params.append(repo_full_name)

        params.append(limit)

        sql = f"""
            SELECT *
            FROM dependabot_alerts
            WHERE {' AND '.join(where_clauses)}
            ORDER BY alert_number ASC
            LIMIT %s
        """

        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [AlertRecord.model_validate(row) for row in rows]

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
                %(research_json)s::jsonb,
                %(assessment_json)s::jsonb
            )
        """

        payload = review.model_dump(mode="python")
        payload["research_json"] = json.dumps(payload["research_json"])
        payload["assessment_json"] = json.dumps(payload["assessment_json"])

        with self.conn.cursor() as cur:
            cur.execute(sql, payload)

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
                needs_review = FALSE,
                last_researched_at = NOW(),
                latest_research_json = %(latest_research_json)s::jsonb,
                updated_at = NOW()
            WHERE alert_id = %(alert_id)s
        """

        payload = {
            "alert_id": alert_id,
            "latest_research_json": json.dumps(latest_research_json),
        }

        with self.conn.cursor() as cur:
            cur.execute(sql, payload)

    def save_review_result(
        self,
        *,
        review: AlertReviewWrite,
        latest_research_json: dict,
    ) -> None:
        self.connect()

        with self.conn.transaction():
            self.insert_review(review)
            self.mark_alert_reviewed(
                alert_id=review.alert_id,
                latest_research_json=latest_research_json,
            )
