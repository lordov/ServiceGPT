"""update message  model +role

Revision ID: 172d18abdc4d
Revises: 3e32a533d985
Create Date: 2025-02-18 11:45:33.425843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '172d18abdc4d'
down_revision: Union[str, None] = '3e32a533d985'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("""
        INSERT INTO users (id, email, hashed_password, role, is_active)
        SELECT 0, 'assistant@servicegpt.com', '', 'assistant', 1
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = 0);
    """))
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column(
        'role', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'role')
    # ### end Alembic commands ###
