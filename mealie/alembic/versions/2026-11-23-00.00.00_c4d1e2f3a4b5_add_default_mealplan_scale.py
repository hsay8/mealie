"""add default_mealplan_scale to household_preferences

Revision ID: c4d1e2f3a4b5
Revises: 08880d089634
Create Date: 2026-11-23 00:00:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c4d1e2f3a4b5"
down_revision: str | None = "08880d089634"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.add_column(sa.Column("default_mealplan_scale", sa.Float(), server_default="1", nullable=False))


def downgrade():
    with op.batch_alter_table("household_preferences", schema=None) as batch_op:
        batch_op.drop_column("default_mealplan_scale")
