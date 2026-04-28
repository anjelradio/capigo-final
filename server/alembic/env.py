import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine, engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from app.modules.assignments.models import RequestAssignment
from app.modules.incidents.models import (
    Evidence,
    IncidentFeedback,
    Incident,
    IncidentServiceReport,
    Problem,
    ProblemServiceMap,
)
from app.modules.repair_shop.models import (
    RepairShop,
    Service,
    ShopInvitation,
    ShopMechanic,
    ShopService,
)
from app.modules.realtime.models import DevicePushToken, IncidentLiveState, IncidentRealtimeEvent
from app.modules.user.models import User, Vehicle
from app.modules.wallet.models import Transactions, Wallet

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
load_dotenv()
# DEV
# DATABASE_URL = os.getenv("DATABASE_URL")


# PROD
raw_url = os.environ["DATABASE_URL"]
url = raw_url
if url.startswith("postgres//"):
    url = "postgresql+psycopg://" + url[len("postgres://") :]
elif url.startswith("postgresql://") and "+psycopg" not in url:
    url = "postgresql+psycopg://" + url[len("postgresql://") :]

DATABASE_URL = url

target_metadata = SQLModel.metadata

POSTGIS_SYSTEM_TABLES = {
    "spatial_ref_sys",
    "geometry_columns",
    "geography_columns",
    "raster_columns",
    "raster_overviews",
}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in POSTGIS_SYSTEM_TABLES:
        return False
    return True

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
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool, future=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
