"""remove param tables

Revision ID: 9187f0fe0730
Revises: 6c3b670fecec
Create Date: 2024-08-19 09:44:30.616361

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9187f0fe0730"
down_revision: Union[str, None] = "6c3b670fecec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("video_params")
    op.drop_table("stitch_params")
    op.alter_column(
        "imaging_events", "system", existing_type=sa.VARCHAR(length=6), nullable=True
    )
    op.alter_column(
        "imaging_events", "system_position", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "imaging_events", "system_position", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "imaging_events", "system", existing_type=sa.VARCHAR(length=6), nullable=False
    )
    op.create_table(
        "stitch_params",
        sa.Column("id", sa.CHAR(length=32), autoincrement=False, nullable=False),
        sa.Column("grid_row", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("grid_col", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "imaging_event_id", sa.CHAR(length=32), autoincrement=False, nullable=False
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["imaging_event_id"],
            ["imaging_events.id"],
            name="stitch_params_imaging_event_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="stitch_params_pkey"),
    )
    op.create_table(
        "video_params",
        sa.Column("id", sa.CHAR(length=32), autoincrement=False, nullable=False),
        sa.Column(
            "imaging_event_id", sa.CHAR(length=32), autoincrement=False, nullable=False
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["imaging_event_id"],
            ["imaging_events.id"],
            name="video_params_imaging_event_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="video_params_pkey"),
    )
    # ### end Alembic commands ###
