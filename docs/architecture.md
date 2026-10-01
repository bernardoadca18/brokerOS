# BrokerOS Architecture

## Product Objective

BrokerOS is a sales operations platform designed for companies that sell vehicle insurance and consortium products. The platform provides a complete CRM solution with lead management, opportunity tracking, customer relationship management, task coordination, and analytics capabilities.

The system is built to support B2B sales teams in their daily operations, from initial lead capture through opportunity closure and ongoing customer relationship management.

## Implemented Modules

### Organizations (Phase 1)
Multi-tenant support is fully implemented. Each organization has:
- Isolated data with tenant-aware queries
- Unique slug-based identification for login
- Independent user management
- Complete data isolation between tenants

### Users (Phase 1)
User management with role-based access control:
- Three roles: admin, manager, sales
- Password hashing with bcrypt
- Email-based authentication
- Organization-scoped user lists

### Authentication (Phase 1)
JWT-based authentication with HttpOnly session cookies:
- Login via organization slug + email + password
- Secure HttpOnly cookies for session management
- Token refresh mechanism
- Current user context injection

## Message Queue Roadmap (Future)

BrokerOS will eventually require a message broker for asynchronous processing. The roadmap includes:

### Phase 2-3: RabbitMQ (Recommended for Initial Implementation)
- **Use Cases**: Email notifications, report generation, background tasks
- **Rationale**: Simpler operational model, well-suited for task queues
- **Integration**: FastAPI with `aio-pika` library
- **Deployment**: Single instance with optional clustering

### Phase 4+: Kafka (For High-Scale Event Streaming)
- **Use Cases**: Event sourcing, real-time analytics, audit logs, inter-service communication
- **Rationale**: Higher throughput, event replay capabilities, better for microservices
- **Integration**: `aiokafka` library with async consumers
- **Deployment**: Multi-broker cluster with Zookeeper or KRaft mode

### Migration Path
1. Start with RabbitMQ for immediate async needs
2. Introduce Kafka alongside RabbitMQ for event streaming
3. Gradually migrate appropriate workloads to Kafka
4. Maintain RabbitMQ for task queues, Kafka for events

**Note**: No message broker implementation in Phase 1. This is documentation only for future planning.

## Planned Domain Modules

The following modules are planned for future implementation phases:

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

## Multi-Tenancy Implementation

Multi-tenancy is fully implemented in Phase 1. All business entities include `organization_id` for tenant isolation:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'sales',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, email)
);
```

Tenant isolation is enforced at the application layer through:
- Organization-scoped database queries in all endpoints
- Tenant-aware authentication requiring organization slug
- Test suite verification of cross-tenant access prevention

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
