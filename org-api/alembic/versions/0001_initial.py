"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["departments.id"],
            name="fk_departments_parent_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_departments_id", "departments", ["id"])
    op.create_index("ix_departments_name", "departments", ["name"])
    op.create_index("ix_departments_parent_id", "departments", ["parent_id"])

    # Unique constraint: name must be unique within the same parent (including root)
    op.create_index(
        "uq_departments_name_parent",
        "departments",
        ["name", "parent_id"],
        unique=True,
        postgresql_where=sa.text("parent_id IS NOT NULL"),
    )
    # Separate partial index for root departments (parent_id IS NULL)
    op.create_index(
        "uq_departments_name_root",
        "departments",
        ["name"],
        unique=True,
        postgresql_where=sa.text("parent_id IS NULL"),
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("position", sa.String(length=200), nullable=False),
        sa.Column("hired_at", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name="fk_employees_department_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employees_id", "employees", ["id"])
    op.create_index("ix_employees_department_id", "employees", ["department_id"])
    op.create_index("ix_employees_full_name", "employees", ["full_name"])


def downgrade() -> None:
    op.drop_table("employees")
    op.drop_index("uq_departments_name_root", table_name="departments")
    op.drop_index("uq_departments_name_parent", table_name="departments")
    op.drop_index("ix_departments_parent_id", table_name="departments")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_index("ix_departments_id", table_name="departments")
    op.drop_table("departments")
