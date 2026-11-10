
import os
import psycopg


def get_db_connection():
    """
    Create a secure connection to the Supabase PostgreSQL database.
    The DATABASE_URL is stored in Vercel environment variables.
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg.connect(
        database_url,
        sslmode="require",
        connect_timeout=10,
        prepare_threshold=None,
    )


def check_database_connection():
    """
    Verify that the research schema is accessible.
    This does not create, change, or delete participant data.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'research'
                    AND table_name = 'participants'
                )
                """
            )
            return cursor.fetchone()[0]
