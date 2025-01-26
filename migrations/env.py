from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import MetaData, Table, Column, String, Integer, create_engine, ForeignKey


from alembic import context
import requests
from sqlalchemy import MetaData
import pickle
import base64

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

METADATA_ENDPOINTS = [
    "http://127.0.0.1:8000/metadata1",  # App1
    "http://127.0.0.1:8001/metadata1",  # App2
]

# Create an empty MetaData instance
unified_metadata = MetaData()

def recreate_columns(table):
    new_columns = []
    for col in table.columns:
        # Check if the column has a ForeignKey
        if col.foreign_keys:
            fk = list(col.foreign_keys)[0]  # Extract the ForeignKey object
            new_columns.append(Column(col.name, col.type, ForeignKey(fk.target_fullname), primary_key=col.primary_key, nullable=col.nullable))
        else:
            # No foreign key, just recreate the column
            new_columns.append(Column(col.name, col.type, primary_key=col.primary_key, nullable=col.nullable))
    return new_columns

def fetch_and_load_metadata():
    """Fetch metadata from applications and load it into SQLAlchemy."""

    try:
        for endpoint in METADATA_ENDPOINTS:
            response = requests.get(endpoint)
            response_json = response.json()
            base64_metadata = response_json.get("metadata")
            pickled_metadata = base64.b64decode(base64_metadata)
            metadata_dict = pickle.loads(pickled_metadata)

            for table_name, table_obj in metadata_dict.items():
                columns = recreate_columns(table_obj)  # Extract and recreate columns
                Table(table_name, unified_metadata, *columns)
            
    except Exception as e:
        print(f"Failed to fetch metadata from {endpoint}: {e}")

# Fetch and load metadata from all applications
fetch_and_load_metadata()
# Print the tables in unified metadata to check
print("Unified Metadata Tables:", unified_metadata.tables)

# Set target_metadata for Alembic
target_metadata = unified_metadata

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
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
