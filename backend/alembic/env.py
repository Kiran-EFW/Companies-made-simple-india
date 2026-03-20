"""Alembic environment configuration.

Imports all SQLAlchemy models and configures the migration environment
to use the database URL from application settings.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import the Base and all models so metadata is fully populated
from src.database import Base
from src.models import (  # noqa: F401
    User,
    Company,
    Director,
    Document,
    Payment,
    StampDutyConfig,
    DSCPricing,
    Task,
    AgentLog,
    Notification,
    NotificationPreference,
    AdminLog,
    InternalNote,
    ComplianceTask,
    Shareholder,
    ShareTransaction,
    ServiceRequest,
    Subscription,
    AccountingConnection,
    ESOPPlan,
    ESOPGrant,
    FundingRound,
    RoundInvestor,
    StakeholderProfile,
    CompanyMember,
)
from src.models.filing_task import FilingTask  # noqa: F401
from src.models.verification_queue import VerificationQueue  # noqa: F401
from src.models.escalation_rule import EscalationRule, EscalationLog  # noqa: F401
from src.models.legal_template import LegalDocument  # noqa: F401
from src.models.statutory_register import StatutoryRegister, RegisterEntry  # noqa: F401
from src.models.meeting import Meeting  # noqa: F401
from src.models.data_room import DataRoomFolder, DataRoomFile, DataRoomShareLink, DataRoomAccessLog  # noqa: F401
from src.models.esign import SignatureRequest, Signatory, SignatureAuditLog  # noqa: F401
from src.models.message import Message  # noqa: F401
from src.models.ca_assignment import CAAssignment  # noqa: F401
from src.models.conversion_event import ConversionEvent  # noqa: F401
from src.models.investor_interest import InvestorInterest  # noqa: F401
from src.models.valuation import Valuation  # noqa: F401

# Import settings to get database URL
from src.config import get_settings

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata from our models
target_metadata = Base.metadata

# Override sqlalchemy.url from application settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

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

    In this scenario we create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
