"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_company_id", "users", ["company_id"], unique=False)
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(64), nullable=True),
        sa.Column("address", sa.String(512), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_locations_company_id", "locations", ["company_id"], unique=False)
    op.create_index("ix_locations_company_name", "locations", ["company_id", "name"], unique=True)
    op.create_table(
        "workers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(128), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(64), nullable=True),
        sa.Column("fcm_token", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workers_company_id", "workers", ["company_id"], unique=False)
    op.create_index("ix_workers_external_id", "workers", ["external_id"], unique=False)
    op.create_table(
        "worker_location_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_worker_location_assignments_worker_id", "worker_location_assignments", ["worker_id"], unique=False)
    op.create_index("ix_worker_location_assignments_location_id", "worker_location_assignments", ["location_id"], unique=False)
    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("message_title", sa.String(255), nullable=False),
        sa.Column("message_body", sa.String(1024), nullable=False),
        sa.Column("send_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedules_location_id", "schedules", ["location_id"], unique=False)
    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(128), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.String(1024), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("error_message", sa.String(512), nullable=True),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_logs_location_id", "notification_logs", ["location_id"], unique=False)
    op.create_index("ix_notification_logs_schedule_id", "notification_logs", ["schedule_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_notification_logs_schedule_id", "notification_logs")
    op.drop_index("ix_notification_logs_location_id", "notification_logs")
    op.drop_table("notification_logs")
    op.drop_index("ix_schedules_location_id", "schedules")
    op.drop_table("schedules")
    op.drop_index("ix_worker_location_assignments_location_id", "worker_location_assignments")
    op.drop_index("ix_worker_location_assignments_worker_id", "worker_location_assignments")
    op.drop_table("worker_location_assignments")
    op.drop_index("ix_workers_external_id", "workers")
    op.drop_index("ix_workers_company_id", "workers")
    op.drop_table("workers")
    op.drop_index("ix_locations_company_name", "locations")
    op.drop_index("ix_locations_company_id", "locations")
    op.drop_table("locations")
    op.drop_index("ix_users_company_id", "users")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
    op.drop_table("companies")
