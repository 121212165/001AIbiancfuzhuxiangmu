"""Add Thinker system tables

Revision ID: 002_add_thinker_tables
Revises: 001_initial
Create Date: 2025-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '002_add_thinker_tables'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create low_quality_pool table
    op.create_table(
        'low_quality_pool',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=500), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('original_score', sa.Float(), nullable=False),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('discovered_at', sa.DateTime(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('processing_attempts', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_low_quality_pool_id'), 'low_quality_pool', ['id'])
    op.create_index(op.f('ix_low_quality_pool_source'), 'low_quality_pool', ['source'], unique=True)
    op.create_index(op.f('ix_low_quality_pool_type'), 'low_quality_pool', ['type'])
    op.create_index(op.f('ix_low_quality_pool_discovered_at'), 'low_quality_pool', ['discovered_at'])
    op.create_index(op.f('ix_low_quality_pool_processed'), 'low_quality_pool', ['processed'])
    op.create_index(op.f('ix_low_quality_pool_original_score'), 'low_quality_pool', ['original_score'])

    # Create insights table
    op.create_table(
        'insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_node_ids', postgresql.JSONB(), nullable=False),
        sa.Column('insight_content', sa.Text(), nullable=False),
        sa.Column('insight_type', sa.String(length=50), nullable=False),
        sa.Column('value_score', sa.Float(), nullable=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('meta_data', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_insights_id'), 'insights', ['id'])
    op.create_index(op.f('ix_insights_insight_type'), 'insights', ['insight_type'])
    op.create_index(op.f('ix_insights_created_at'), 'insights', ['created_at'])
    op.create_index(op.f('ix_insights_value_score'), 'insights', ['value_score'])

    # Create thinking_processes table
    op.create_table(
        'thinking_processes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=False),
        sa.Column('input_low_quality_ids', postgresql.JSONB(), nullable=False),
        sa.Column('thinking_prompt', sa.Text(), nullable=True),
        sa.Column('thinking_result', sa.Text(), nullable=True),
        sa.Column('extracted_insights', postgresql.JSONB(), nullable=True),
        sa.Column('new_frontier_seeds', postgresql.JSONB(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_thinking_processes_id'), 'thinking_processes', ['id'])
    op.create_index(op.f('ix_thinking_processes_session_type'), 'thinking_processes', ['session_type'])
    op.create_index(op.f('ix_thinking_processes_created_at'), 'thinking_processes', ['created_at'])


def downgrade() -> None:
    op.drop_index(op.f('ix_thinking_processes_created_at'), table_name='thinking_processes')
    op.drop_index(op.f('ix_thinking_processes_session_type'), table_name='thinking_processes')
    op.drop_index(op.f('ix_thinking_processes_id'), table_name='thinking_processes')
    op.drop_table('thinking_processes')

    op.drop_index(op.f('ix_insights_value_score'), table_name='insights')
    op.drop_index(op.f('ix_insights_created_at'), table_name='insights')
    op.drop_index(op.f('ix_insights_insight_type'), table_name='insights')
    op.drop_index(op.f('ix_insights_id'), table_name='insights')
    op.drop_table('insights')

    op.drop_index(op.f('ix_low_quality_pool_original_score'), table_name='low_quality_pool')
    op.drop_index(op.f('ix_low_quality_pool_processed'), table_name='low_quality_pool')
    op.drop_index(op.f('ix_low_quality_pool_discovered_at'), table_name='low_quality_pool')
    op.drop_index(op.f('ix_low_quality_pool_type'), table_name='low_quality_pool')
    op.drop_index(op.f('ix_low_quality_pool_source'), table_name='low_quality_pool')
    op.drop_index(op.f('ix_low_quality_pool_id'), table_name='low_quality_pool')
    op.drop_table('low_quality_pool')
