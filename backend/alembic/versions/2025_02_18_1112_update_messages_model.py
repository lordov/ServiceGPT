"""update chat model

Revision ID: 3e32a533d985
Revises: 2656035e96fc
Create Date: 2025-02-18 11:12:15.408094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '3e32a533d985'
down_revision: Union[str, None] = '2656035e96fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('messages', 'content',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=1000),
               type_=sa.Text(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('messages', 'content',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(collation='utf8mb4_general_ci', length=1000),
               existing_nullable=False)
    # ### end Alembic commands ###
