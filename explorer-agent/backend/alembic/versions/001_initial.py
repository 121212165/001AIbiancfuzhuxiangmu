"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2025-12-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # Create nodes table
    op.create_table(
        'nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=500), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('embedding', sa.String(), nullable=True),  # Will be Vector type
        sa.Column('value_score', sa.Float(), nullable=True),
        sa.Column('discovered_at', sa.DateTime(), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nodes_id'), 'nodes', ['id'])
    op.create_index(op.f('ix_nodes_source'), 'nodes', ['source'], unique=True)
    op.create_index(op.f('ix_nodes_type'), 'nodes', ['type'])
    op.create_index(op.f('ix_nodes_discovered_at'), 'nodes', ['discovered_at'])
    op.create_index(op.f('ix_nodes_value_score'), 'nodes', ['value_score'])

    # Create exploration_paths table
    op.create_table(
        'exploration_paths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path', sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_value', sa.Float(), nullable=True),
        sa.Column('strategy', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exploration_paths_id'), 'exploration_paths', ['id'])
    op.create_index(op.f('ix_exploration_paths_started_at'), 'exploration_paths', ['started_at'])

    # Create frontier table
    op.create_table(
        'frontier',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seed', sa.String(length=500), nullable=False),
        sa.Column('priority', sa.Float(), nullable=True),
        sa.Column('source_node_id', sa.Integer(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_node_id'], ['nodes.id'])
    )
    op.create_index(op.f('ix_frontier_id'), 'frontier', ['id'])
    op.create_index(op.f('ix_frontier_seed'), 'frontier', ['seed'], unique=True)
    op.create_index(op.f('ix_frontier_priority'), 'frontier', ['priority'])

    # Create edges table
    op.create_table(
        'edges',
        sa.Column('from_node_id', sa.Integer(), primary_key=True),
        sa.Column('to_node_id', sa.Integer(), primary_key=True),
        sa.Column('relationship', sa.String(length=50), nullable=False),
        sa.Column('strength', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['from_node_id'], ['nodes.id']),
        sa.ForeignKeyConstraint(['to_node_id'], ['nodes.id'])
    )


def downgrade() -> None:
    op.drop_table('edges')
    op.drop_table('frontier')
    op.drop_index(op.f('ix_exploration_paths_started_at'), table_name='exploration_paths')
    op.drop_index(op.f('ix_exploration_paths_id'), table_name='exploration_paths')
    op.drop_table('exploration_paths')
    op.drop_index(op.f('ix_nodes_value_score'), table_name='nodes')
    op.drop_index(op.f('ix_nodes_discovered_at'), table_name='nodes')
    op.drop_index(op.f('ix_nodes_type'), table_name='nodes')
    op.drop_index(op.f('ix_nodes_source'), table_name='nodes')
    op.drop_index(op.f('ix_nodes_id'), table_name='nodes')
    op.drop_table('nodes')
