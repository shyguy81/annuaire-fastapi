"""Add RelationshipProfile, Interaction, and RelationshipAction models

Revision ID: 001_add_rap_models
Revises: 
Create Date: 2026-05-30 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_rap_models'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    relationshiptype_enum = sa.Enum(
        'spouse', 'family', 'business', 'mentor', 'friend', 'acquaintance',
        name='relationshiptype'
    )
    proximitytype_enum = sa.Enum(
        'cold', 'warm', 'active', 'close',
        name='proximitytype'
    )
    businesspotential_enum = sa.Enum(
        'low', 'medium', 'high',
        name='businesspotential'
    )
    interactiontype_enum = sa.Enum(
        'call', 'email', 'meeting', 'message', 'other',
        name='interactiontype'
    )
    actiontype_enum = sa.Enum(
        'followup', 'relance', 'candidature', 'email', 'call', 'meeting',
        name='actiontype'
    )
    actionstatus_enum = sa.Enum(
        'todo', 'in_progress', 'completed', 'cancelled',
        name='actionstatus'
    )
    priority_enum = sa.Enum(
        'low', 'medium', 'high',
        name='priority'
    )

    relationshiptype_enum.create(op.get_bind())
    proximitytype_enum.create(op.get_bind())
    businesspotential_enum.create(op.get_bind())
    interactiontype_enum.create(op.get_bind())
    actiontype_enum.create(op.get_bind())
    actionstatus_enum.create(op.get_bind())
    priority_enum.create(op.get_bind())

    # Create relationship_profiles table
    op.create_table(
        'relationship_profiles',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('contact_id', sa.String(36), nullable=False),
        sa.Column('relationship_type', sa.Enum('spouse', 'family', 'business', 'mentor', 'friend', 'acquaintance', name='relationshiptype'), nullable=False),
        sa.Column('proximity_level', sa.Enum('cold', 'warm', 'active', 'close', name='proximitytype'), nullable=False),
        sa.Column('trust_level', sa.Integer(), nullable=False),
        sa.Column('business_potential', sa.Enum('low', 'medium', 'high', name='businesspotential'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_relationship_profiles_contact_id'), 'relationship_profiles', ['contact_id'], unique=False)

    # Create interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('contact_id', sa.String(36), nullable=False),
        sa.Column('interaction_type', sa.Enum('call', 'email', 'meeting', 'message', 'other', name='interactiontype'), nullable=False),
        sa.Column('interaction_date', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interactions_contact_id'), 'interactions', ['contact_id'], unique=False)

    # Create relationship_actions table
    op.create_table(
        'relationship_actions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('contact_id', sa.String(36), nullable=False),
        sa.Column('action_type', sa.Enum('followup', 'relance', 'candidature', 'email', 'call', 'meeting', name='actiontype'), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', name='priority'), nullable=False),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'completed', 'cancelled', name='actionstatus'), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_relationship_actions_contact_id'), 'relationship_actions', ['contact_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_relationship_actions_contact_id'), table_name='relationship_actions')
    op.drop_index(op.f('ix_interactions_contact_id'), table_name='interactions')
    op.drop_index(op.f('ix_relationship_profiles_contact_id'), table_name='relationship_profiles')

    # Drop tables
    op.drop_table('relationship_actions')
    op.drop_table('interactions')
    op.drop_table('relationship_profiles')

    # Drop enums
    sa.Enum('todo', 'in_progress', 'completed', 'cancelled', name='actionstatus').drop(op.get_bind())
    sa.Enum('followup', 'relance', 'candidature', 'email', 'call', 'meeting', name='actiontype').drop(op.get_bind())
    sa.Enum('call', 'email', 'meeting', 'message', 'other', name='interactiontype').drop(op.get_bind())
    sa.Enum('low', 'medium', 'high', name='businesspotential').drop(op.get_bind())
    sa.Enum('cold', 'warm', 'active', 'close', name='proximitytype').drop(op.get_bind())
    sa.Enum('spouse', 'family', 'business', 'mentor', 'friend', 'acquaintance', name='relationshiptype').drop(op.get_bind())
    sa.Enum('low', 'medium', 'high', name='priority').drop(op.get_bind())
