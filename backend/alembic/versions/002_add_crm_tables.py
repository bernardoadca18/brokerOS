"""add crm tables

Revision ID: 002
Revises: 001_add_organizations_and_users
Create Date: 2026-10-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_add_organizations_and_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types for PostgreSQL
    lead_source = postgresql.ENUM(
        'manual', 'website', 'referral', 'whatsapp', 'campaign', 'other',
        name='lead_source',
        create_type=False
    )
    lead_status = postgresql.ENUM(
        'new', 'contacted', 'qualified', 'unqualified', 'converted',
        name='lead_status',
        create_type=False
    )
    product_interest = postgresql.ENUM(
        'vehicle_insurance', 'consortium',
        name='product_interest',
        create_type=False
    )
    customer_type = postgresql.ENUM(
        'individual', 'company',
        name='customer_type',
        create_type=False
    )
    opportunity_stage = postgresql.ENUM(
        'qualification', 'proposal', 'negotiation', 'won', 'lost',
        name='opportunity_stage',
        create_type=False
    )
    product_type = postgresql.ENUM(
        'vehicle_insurance', 'consortium',
        name='product_type',
        create_type=False
    )

    # Create enum types
    op.execute("CREATE TYPE lead_source AS ENUM ('manual', 'website', 'referral', 'whatsapp', 'campaign', 'other')")
    op.execute("CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'unqualified', 'converted')")
    op.execute("CREATE TYPE product_interest AS ENUM ('vehicle_insurance', 'consortium')")
    op.execute("CREATE TYPE customer_type AS ENUM ('individual', 'company')")
    op.execute("CREATE TYPE opportunity_stage AS ENUM ('qualification', 'proposal', 'negotiation', 'won', 'lost')")
    op.execute("CREATE TYPE product_type AS ENUM ('vehicle_insurance', 'consortium')")

    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('product_interest', product_interest, nullable=False),
        sa.Column('source', lead_source, nullable=False),
        sa.Column('status', lead_status, nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leads_organization_id', 'leads', ['organization_id'])
    op.create_index('ix_leads_owner_id', 'leads', ['owner_id'])
    op.create_index('ix_leads_status', 'leads', ['status'])
    op.create_index('ix_leads_org_status', 'leads', ['organization_id', 'status'])
    op.create_index('ix_leads_org_owner', 'leads', ['organization_id', 'owner_id'])
    op.create_index('ix_leads_org_created', 'leads', ['organization_id', 'created_at'])

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('customer_type', customer_type, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_customers_organization_id', 'customers', ['organization_id'])
    op.create_index('ix_customers_owner_id', 'customers', ['owner_id'])
    op.create_index('ix_customers_org_owner', 'customers', ['organization_id', 'owner_id'])
    op.create_index('ix_customers_org_created', 'customers', ['organization_id', 'created_at'])

    # Create opportunities table
    op.create_table(
        'opportunities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('customer_id', sa.UUID(), nullable=False),
        sa.Column('lead_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('product_type', product_type, nullable=False),
        sa.Column('stage', opportunity_stage, nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('expected_close_date', sa.Date(), nullable=True),
        sa.Column('lost_reason', sa.String(length=500), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lead_id')
    )
    op.create_index('ix_opportunities_organization_id', 'opportunities', ['organization_id'])
    op.create_index('ix_opportunities_owner_id', 'opportunities', ['owner_id'])
    op.create_index('ix_opportunities_stage', 'opportunities', ['stage'])
    op.create_index('ix_opportunities_customer_id', 'opportunities', ['customer_id'])
    op.create_index('ix_opportunities_org_stage', 'opportunities', ['organization_id', 'stage'])
    op.create_index('ix_opportunities_org_owner', 'opportunities', ['organization_id', 'owner_id'])
    op.create_index('ix_opportunities_org_created', 'opportunities', ['organization_id', 'created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_opportunities_org_created', table_name='opportunities')
    op.drop_index('ix_opportunities_org_owner', table_name='opportunities')
    op.drop_index('ix_opportunities_org_stage', table_name='opportunities')
    op.drop_index('ix_opportunities_customer_id', table_name='opportunities')
    op.drop_index('ix_opportunities_stage', table_name='opportunities')
    op.drop_index('ix_opportunities_owner_id', table_name='opportunities')
    op.drop_index('ix_opportunities_organization_id', table_name='opportunities')
    op.drop_table('opportunities')

    op.drop_index('ix_customers_org_created', table_name='customers')
    op.drop_index('ix_customers_org_owner', table_name='customers')
    op.drop_index('ix_customers_owner_id', table_name='customers')
    op.drop_index('ix_customers_organization_id', table_name='customers')
    op.drop_table('customers')

    op.drop_index('ix_leads_org_created', table_name='leads')
    op.drop_index('ix_leads_org_owner', table_name='leads')
    op.drop_index('ix_leads_org_status', table_name='leads')
    op.drop_index('ix_leads_status', table_name='leads')
    op.drop_index('ix_leads_owner_id', table_name='leads')
    op.drop_index('ix_leads_organization_id', table_name='leads')
    op.drop_table('leads')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS product_type')
    op.execute('DROP TYPE IF EXISTS opportunity_stage')
    op.execute('DROP TYPE IF EXISTS customer_type')
    op.execute('DROP TYPE IF EXISTS product_interest')
    op.execute('DROP TYPE IF EXISTS lead_status')
    op.execute('DROP TYPE IF EXISTS lead_source')
