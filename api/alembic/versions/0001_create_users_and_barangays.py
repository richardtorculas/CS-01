"""create_users_and_barangays

Revision ID: 0001
Revises:
Create Date: 2026-09-26 11:07:51.669925
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "barangays",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_barangays")),
        sa.UniqueConstraint("name", name=op.f("uq_barangays_name")),
    )
    op.create_table(
        "users",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("mobile", sa.String(length=16), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("barangay_id", sa.Uuid(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role", sa.Enum("RESIDENT", "PERSONNEL", "ADMIN", name="user_role"), nullable=False
        ),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["barangay_id"], ["barangays.id"], name=op.f("fk_users_barangay_id_barangays")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("mobile", name=op.f("uq_users_mobile")),
    )
    op.create_index(op.f("ix_users_barangay_id"), "users", ["barangay_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_barangay_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("barangays")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
