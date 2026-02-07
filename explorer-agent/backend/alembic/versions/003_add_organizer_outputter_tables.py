"""Add Organizer and Outputter system tables

Revision ID: 003_add_organizer_outputter_tables
Revises: 002_add_thinker_tables
Create Date: 2025-12-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '003_add_organizer_outputter_tables'
down_revision = '002_add_thinker_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # Organizer Tables
    # ============================================================

    # Knowledge graph nodes table
    op.create_table(
        'knowledge_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(length=50), nullable=False, comment='paper, concept, author, insight, method, dataset'),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('source_node_id', sa.Integer(), nullable=True, comment='Reference to original node or insight'),
        sa.Column('source_type', sa.String(length=50), nullable=True, comment='node or insight'),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_nodes_id'), 'knowledge_nodes', ['id'])
    op.create_index(op.f('ix_knowledge_nodes_type'), 'knowledge_nodes', ['node_type'])
    op.create_index(op.f('ix_knowledge_nodes_source'), 'knowledge_nodes', ['source_node_id'])

    # Knowledge graph edges table
    op.create_table(
        'knowledge_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False, comment='knowledge_nodes.id'),
        sa.Column('target_id', sa.Integer(), nullable=False, comment='knowledge_nodes.id'),
        sa.Column('edge_type', sa.String(length=50), nullable=False, comment='cites, discusses, uses, applies_to, related_to, etc.'),
        sa.Column('weight', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_edges_id'), 'knowledge_edges', ['id'])
    op.create_index(op.f('ix_knowledge_edges_source_target'), 'knowledge_edges', ['source_id', 'target_id'])
    op.create_index(op.f('ix_knowledge_edges_type'), 'knowledge_edges', ['edge_type'])

    # Topic clusters table
    op.create_table(
        'topic_clusters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cluster_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('item_ids', postgresql.ARRAY(sa.Integer()), nullable=True, comment='Node and insight IDs in this cluster'),
        sa.Column('cluster_center', postgresql.ARRAY(sa.Float()), nullable=True, comment='Cluster center vector'),
        sa.Column('item_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('confidence', sa.Float(), nullable=True, comment='Cluster confidence score'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topic_clusters_id'), 'topic_clusters', ['id'])
    op.create_index(op.f('ix_topic_clusters_name'), 'topic_clusters', ['cluster_name'])

    # Timeline events table
    op.create_table(
        'timeline_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=True, comment='breakthrough, publication, trend_change'),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('related_node_ids', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('impact_level', sa.String(length=20), nullable=True, comment='high, medium, low'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timeline_events_id'), 'timeline_events', ['id'])
    op.create_index(op.f('ix_timeline_events_date'), 'timeline_events', ['event_date'])
    op.create_index(op.f('ix_timeline_events_type'), 'timeline_events', ['event_type'])

    # Trend metrics table
    op.create_table(
        'trend_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('keyword', sa.String(length=100), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('trend_direction', sa.String(length=20), nullable=True, comment='rising, stable, declining'),
        sa.Column('score', sa.Float(), nullable=True, comment='Trend score'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trend_metrics_id'), 'trend_metrics', ['id'])
    op.create_index(op.f('ix_trend_metrics_keyword_date'), 'trend_metrics', ['keyword', 'metric_date'])

    # Research questions table
    op.create_table(
        'research_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=True, comment='gap, contradiction, opportunity'),
        sa.Column('context', postgresql.JSONB(), nullable=True),
        sa.Column('importance', sa.String(length=20), nullable=True, comment='high, medium, low'),
        sa.Column('suggested_exploration', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='open', comment='open, answered'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_questions_id'), 'research_questions', ['id'])
    op.create_index(op.f('ix_research_questions_status'), 'research_questions', ['status'])
    op.create_index(op.f('ix_research_questions_importance'), 'research_questions', ['importance'])

    # ============================================================
    # Outputter Tables
    # ============================================================

    # Generated reports table
    op.create_table(
        'generated_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False, comment='daily, weekly, insight_brief'),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=True, server_default='markdown', comment='markdown, html, json'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True, comment='Generated file path'),
        sa.Column('feedback_to_explorer', postgresql.JSONB(), nullable=True, comment='Suggestions for exploration optimization'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_reports_id'), 'generated_reports', ['id'])
    op.create_index(op.f('ix_generated_reports_type'), 'generated_reports', ['report_type'])
    op.create_index(op.f('ix_generated_reports_created'), 'generated_reports', ['created_at'])


def downgrade() -> None:
    # Outputter tables
    op.drop_index(op.f('ix_generated_reports_created'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_type'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_id'), table_name='generated_reports')
    op.drop_table('generated_reports')

    # Organizer tables
    op.drop_index(op.f('ix_research_questions_importance'), table_name='research_questions')
    op.drop_index(op.f('ix_research_questions_status'), table_name='research_questions')
    op.drop_index(op.f('ix_research_questions_id'), table_name='research_questions')
    op.drop_table('research_questions')

    op.drop_index(op.f('ix_trend_metrics_keyword_date'), table_name='trend_metrics')
    op.drop_index(op.f('ix_trend_metrics_id'), table_name='trend_metrics')
    op.drop_table('trend_metrics')

    op.drop_index(op.f('ix_timeline_events_type'), table_name='timeline_events')
    op.drop_index(op.f('ix_timeline_events_date'), table_name='timeline_events')
    op.drop_index(op.f('ix_timeline_events_id'), table_name='timeline_events')
    op.drop_table('timeline_events')

    op.drop_index(op.f('ix_topic_clusters_name'), table_name='topic_clusters')
    op.drop_index(op.f('ix_topic_clusters_id'), table_name='topic_clusters')
    op.drop_table('topic_clusters')

    op.drop_index(op.f('ix_knowledge_edges_type'), table_name='knowledge_edges')
    op.drop_index(op.f('ix_knowledge_edges_source_target'), table_name='knowledge_edges')
    op.drop_index(op.f('ix_knowledge_edges_id'), table_name='knowledge_edges')
    op.drop_table('knowledge_edges')

    op.drop_index(op.f('ix_knowledge_nodes_source'), table_name='knowledge_nodes')
    op.drop_index(op.f('ix_knowledge_nodes_type'), table_name='knowledge_nodes')
    op.drop_index(op.f('ix_knowledge_nodes_id'), table_name='knowledge_nodes')
    op.drop_table('knowledge_nodes')
