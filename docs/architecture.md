# BrokerOS Architecture

## Product Objective

BrokerOS is a sales operations platform designed for companies that sell vehicle insurance and consortium products. The platform provides a complete CRM solution with lead management, opportunity tracking, customer relationship management, task coordination, and analytics capabilities.

The system is built to support B2B sales teams in their daily operations, from initial lead capture through opportunity closure and ongoing customer relationship management.

## Planned Domain Modules

The following modules are planned for future implementation phases:

### Organizations
Multi-tenant support allowing multiple companies to use the platform independently. Each organization will have isolated data, custom branding options, and independent user management.

### Users
User management with role-based access control. Users belong to organizations and have permissions based on their role (administrator, manager, sales representative, etc.).

### Leads
Lead capture and qualification system. Includes lead sources, scoring, assignment rules, and qualification workflows to convert leads into opportunities.

### Customers
Customer database with complete profiles, policy information, interaction history, and renewal tracking. Supports both individual and corporate customers.

### Opportunities
Sales pipeline management with customizable stages. Tracks opportunities from initial qualification through negotiation to closure, with probability estimates and expected values.

### Tasks
Task and follow-up management integrated with leads, opportunities, and customers. Supports due dates, priorities, assignments, and completion tracking.

### Activities
Activity log tracking all interactions with leads and customers including calls, emails, meetings, and notes. Provides a complete history of customer relationships.

### Analytics
Reporting and analytics dashboards providing insights into sales performance, conversion rates, pipeline health, and team productivity.

### Renewals
Renewal management for insurance policies and consortium contracts. Alerts for upcoming renewals and tracking of renewal success rates.

## Architectural Principles

### Modular Monolith
The system is built as a modular monolith during the initial phases. This provides:
- Simplified deployment and operations
- Strong consistency within a single database
- Easier refactoring as the domain evolves
- Lower operational overhead compared to microservices

Future transition to microservices is possible if scale demands it, but the initial architecture prioritizes simplicity and development velocity.

### REST API
The backend exposes a RESTful API with clear resource boundaries. The API follows:
- Resource-oriented endpoints
- Consistent error handling
- Versioning through URL paths (/api/v1/)
- OpenAPI documentation

### PostgreSQL
PostgreSQL serves as the primary data store, providing:
- ACID compliance for financial data
- Strong relational integrity
- JSON support for flexible schemas when needed
- Full-text search capabilities

### Tenant-Aware Domain Design
All business entities are designed with multi-tenancy in mind:

```
Business Entity
├── id (primary key)
├── organization_id (tenant identifier)
├── ... (entity-specific fields)
└── timestamps (created_at, updated_at)
```

This design ensures complete data isolation between organizations without requiring separate databases per tenant.

### Frontend/Backend Separation
The frontend (Next.js) and backend (FastAPI) are separate applications:

- Frontend handles UI/UX, routing, and client-side interactions
- Backend handles business logic, data persistence, and API endpoints
- Communication via REST API with JSON payloads

This separation allows independent deployment, scaling, and development of each layer.

### Background Jobs (When Necessary)
Background job processing will be introduced only when required for:
- Long-running operations (report generation, data imports)
- External integrations with retry requirements
- Scheduled tasks (renewal reminders, follow-up notifications)

The framework choice will depend on scale requirements (Celery, RQ, or simpler alternatives).

### External Integrations Isolated Behind Adapters
All external integrations are isolated behind adapter interfaces:

```
Application Code → Interface → Adapter → External Service
```

This pattern allows:
- Easy testing with mock adapters
- Swapping providers without changing application code
- Centralized error handling and retry logic

## Future Multi-Tenancy

Business entities will eventually include `organization_id` for tenant isolation:

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Row-level security policies will enforce tenant isolation
CREATE POLICY tenant_isolation ON leads
    USING (organization_id = current_setting('app.current_organization')::UUID);
```

**Note:** Multi-tenancy is documented but not implemented in Phase 0.

## Technology Stack

### Frontend
- **Framework:** Next.js 15 with App Router
- **Language:** TypeScript
- **Styling:** Tailwind CSS with CSS variables
- **UI Components:** shadcn/ui (Radix primitives)
- **State:** React Server Components + Client Components as needed

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.12+
- **ORM:** SQLAlchemy 2.0 with async support
- **Migrations:** Alembic
- **Validation:** Pydantic v2

### Database
- **Primary:** PostgreSQL 16

### Infrastructure
- **Local Development:** Docker Compose
- **API Documentation:** OpenAPI/Swagger UI (via FastAPI)

## Development Workflow

1. Start PostgreSQL via Docker Compose
2. Run database migrations
3. Start backend API server
4. Start frontend development server
5. Access application at http://localhost:3000

## Deployment Considerations (Future)

Future phases will address:
- Container orchestration (Docker, potentially Kubernetes at scale)
- CI/CD pipelines
- Environment management (staging, production)
- Monitoring and observability
- Backup and disaster recovery
- Security hardening

Phase 0 focuses on local development foundation only.
