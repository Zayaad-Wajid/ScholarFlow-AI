"""Database session management."""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_development_columns()


def ensure_development_columns() -> None:
    inspector = inspect(engine)
    ensure_research_project_columns(inspector)
    ensure_document_columns(inspector)
    ensure_report_columns(inspector)


def ensure_research_project_columns(inspector) -> None:
    if not inspector.has_table("research_projects"):
        return
    columns = {column["name"] for column in inspector.get_columns("research_projects")}
    statements = []
    if "topic" not in columns:
        statements.append("ALTER TABLE research_projects ADD COLUMN topic VARCHAR(255)")
    if "status" not in columns:
        statements.append(
            "ALTER TABLE research_projects "
            "ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'active'"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_document_columns(inspector) -> None:
    if not inspector.has_table("documents"):
        return

    columns = {column["name"] for column in inspector.get_columns("documents")}
    statements = []
    if "user_id" not in columns:
        statements.append("ALTER TABLE documents ADD COLUMN user_id INTEGER")
        statements.append(
            "UPDATE documents "
            "SET user_id = research_projects.user_id "
            "FROM research_projects "
            "WHERE documents.project_id = research_projects.id"
        )
        statements.append("ALTER TABLE documents ALTER COLUMN user_id SET NOT NULL")
        statements.append(
            "ALTER TABLE documents "
            "ADD CONSTRAINT fk_documents_user_id FOREIGN KEY (user_id) REFERENCES users(id)"
        )
        statements.append("CREATE INDEX IF NOT EXISTS ix_documents_user_id ON documents (user_id)")
    if "file_type" not in columns:
        statements.append("ALTER TABLE documents ADD COLUMN file_type VARCHAR(50)")
        statements.append("UPDATE documents SET file_type = 'application/pdf' WHERE file_type IS NULL")
        statements.append("ALTER TABLE documents ALTER COLUMN file_type SET NOT NULL")
    if "extracted_text" not in columns:
        statements.append("ALTER TABLE documents ADD COLUMN extracted_text TEXT")
    if "page_count" not in columns:
        statements.append("ALTER TABLE documents ADD COLUMN page_count INTEGER")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_report_columns(inspector) -> None:
    if not inspector.has_table("reports"):
        return

    columns = {column["name"] for column in inspector.get_columns("reports")}
    statements = []
    if "user_id" not in columns:
        statements.append("ALTER TABLE reports ADD COLUMN user_id INTEGER")
        statements.append(
            "UPDATE reports "
            "SET user_id = research_projects.user_id "
            "FROM research_projects "
            "WHERE reports.project_id = research_projects.id"
        )
        statements.append("ALTER TABLE reports ALTER COLUMN user_id SET NOT NULL")
        statements.append(
            "ALTER TABLE reports "
            "ADD CONSTRAINT fk_reports_user_id FOREIGN KEY (user_id) REFERENCES users(id)"
        )
        statements.append("CREATE INDEX IF NOT EXISTS ix_reports_user_id ON reports (user_id)")
    if "report_type" not in columns:
        statements.append("ALTER TABLE reports ADD COLUMN report_type VARCHAR(50)")
        statements.append("UPDATE reports SET report_type = 'summary' WHERE report_type IS NULL")
        statements.append("ALTER TABLE reports ALTER COLUMN report_type SET NOT NULL")
    if "topic" not in columns:
        statements.append("ALTER TABLE reports ADD COLUMN topic VARCHAR(255)")
        statements.append(
            "UPDATE reports "
            "SET topic = COALESCE(research_projects.topic, research_projects.title, reports.title) "
            "FROM research_projects "
            "WHERE reports.project_id = research_projects.id"
        )
        statements.append("UPDATE reports SET topic = title WHERE topic IS NULL")
        statements.append("ALTER TABLE reports ALTER COLUMN topic SET NOT NULL")
    if "status" in columns:
        statements.append("UPDATE reports SET status = 'completed' WHERE status IS NULL OR status = 'draft'")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
