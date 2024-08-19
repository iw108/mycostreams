"""add data archive entry table

Revision ID: 8e4ca8eaeea7
Revises: 9187f0fe0730
Create Date: 2024-08-19 11:48:47.493400

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e4ca8eaeea7"
down_revision: Union[str, None] = "9187f0fe0730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "data_archive_entries",
        sa.Column("id", sa.Uuid(native_uuid=False), nullable=False),
        sa.Column(
            "type",
            sa.Enum("STITCH", "VIDEO", name="eventtype", native_enum=False),
            nullable=False,
        ),
        sa.Column("experiment_id", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "data_archive_members",
        sa.Column("data_archive_entry_id", sa.Uuid(native_uuid=False), nullable=False),
    )
    op.create_foreign_key(
        None,
        "data_archive_members",
        "data_archive_entries",
        ["data_archive_entry_id"],
        ["id"],
    )
    op.drop_column("data_archive_members", "key")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "data_archive_members",
        sa.Column("key", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "data_archive_members", type_="foreignkey")
    op.drop_column("data_archive_members", "data_archive_entry_id")
    op.drop_table("data_archive_entries")
    # ### end Alembic commands ###