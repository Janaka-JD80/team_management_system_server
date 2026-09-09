from logging.config import fileConfig
from datetime import datetime
from pathlib import Path
import re

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

from app.config import settings
from app.db.base import Base
from app.models import *

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_sync_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    return url

config.set_main_option("sqlalchemy.url", get_sync_database_url())

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def _next_revision_id() -> str:
    """Generate revision id as YYYYMMDD + 4-digit sequence."""
    today = datetime.now().strftime("%Y%m%d")
    versions_dir = Path(__file__).resolve().parent / "versions"
    pattern = re.compile(r"revision:\s*str\s*=\s*['\"](\d+)['\"]")
    max_seq = 0

    for migration_file in versions_dir.glob("*.py"):
        content = migration_file.read_text(encoding="utf-8")
        match = pattern.search(content)
        if not match:
            continue
        rev = match.group(1)
        if rev.startswith(today) and len(rev) >= 12:
            seq = int(rev[8:12])
            max_seq = max(max_seq, seq)

    return f"{today}{max_seq + 1:04d}"


def _process_revision_directives(context, revision, directives):
    if not directives:
        return
    script = directives[0]
    script.rev_id = _next_revision_id()

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=_process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=_process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
