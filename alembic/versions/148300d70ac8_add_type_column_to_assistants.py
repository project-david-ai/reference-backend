import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "148300d70ac8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the column with a default value first
    op.add_column(
        "assistants",
        sa.Column(
            "type", sa.String(length=50), nullable=False, server_default="default_value"
        ),
    )

    # Remove the server default constraint
    with op.batch_alter_table("assistants") as batch_op:
        batch_op.alter_column("type", server_default=None)


def downgrade():
    # Reverse the upgrade steps
    with op.batch_alter_table("assistants") as batch_op:
        batch_op.drop_column("type")
