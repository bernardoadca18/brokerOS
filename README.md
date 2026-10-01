# BrokerOS

**Sales Operations Platform for Insurance and Consortium Businesses**

BrokerOS is a professional B2B sales operations platform designed for companies that sell vehicle insurance and consortium products. It provides comprehensive tools for lead management, opportunity tracking, customer relationship management, task coordination, and sales analytics.

## Current Development Phase

**Phase 1 - Complete ✅**

Phase 1 establishes the authentication and multi-tenant foundation:
- Multi-tenant organization support with data isolation
- User management with role-based access control (admin, manager, sales)
- JWT authentication with HttpOnly session cookies
- Secure password hashing with bcrypt
- Complete test suite with tenant isolation verification
- Database-agnostic UUID support (PostgreSQL and SQLite)

Business modules (CRM, leads, pipeline, etc.) will be implemented in Phase 2+.

## Architecture Overview

BrokerOS follows a modular monolith architecture with clear separation between frontend and backend:

- **Frontend:** Next.js 15 with App Router, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, Python 3.12+, SQLAlchemy 2.0, Alembic
- **Database:** PostgreSQL 16

See [docs/architecture.md](docs/architecture.md) for detailed architectural decisions.

## Tech Stack

### Frontend
- Next.js 15 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui (Radix primitives)
- Lucide React (icons)

### Backend
- FastAPI
- Python 3.12+
- Pydantic v2
- SQLAlchemy 2.0 (async)
- Alembic (migrations)
- asyncpg (PostgreSQL driver)

### Infrastructure
- Docker Compose for local development
- PostgreSQL 16

## Repository Structure

```
brokeros/
├── frontend/           # Next.js application
│   ├── app/           # App router pages
│   ├── components/    # React components
│   │   ├── ui/       # Base UI components
│   │   ├── layout/   # Layout components
│   │   └── shared/   # Shared components
│   ├── lib/          # Utilities and helpers
│   ├── hooks/        # Custom React hooks
│   └── types/        # TypeScript types
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Configuration, security
│   │   ├── db/       # Database models, sessions
│   │   └── modules/  # Domain modules (future)
│   ├── tests/        # Test suite
│   └── alembic/      # Database migrations
├── docs/             # Documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## Local Development

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ and npm
- Python 3.12+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd brokeros
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

3. **Start PostgreSQL**
   ```bash
   docker compose up -d
   ```

4. **Start the backend**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -e ".[dev]"

   # Run the API
   uvicorn app.main:app --reload --port 8000
   ```

5. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Run development server
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Environment Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://brokeros:brokeros_dev@localhost:5432/brokeros` |
| `ENVIRONMENT` | Application environment | `development` |
| `API_PORT` | Backend API port | `8000` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |

## Available Routes

| Route | Description | Status |
|-------|-------------|--------|
| `/` | Redirects to Overview | ✅ Active |
| `/overview` | Dashboard with KPIs and activity | ✅ Placeholder |
| `/leads` | Lead management | ✅ Placeholder |
| `/pipeline` | Sales pipeline | ✅ Placeholder |
| `/customers` | Customer database | ✅ Placeholder |
| `/tasks` | Task management | ✅ Placeholder |
| `/analytics` | Sales analytics | ✅ Placeholder |
| `/settings` | Application settings | ✅ Placeholder |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |

## Development Commands

### Frontend

```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Production build
npm run build

# Start production server
npm run start
```

### Backend

```bash
cd backend

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy app

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Current Limitations

Phase 0 is intentionally limited to foundation work:

- ❌ No authentication or authorization
- ❌ No business modules implemented
- ❌ No database schema beyond health check
- ❌ No real data or integrations
- ❌ No production deployment configuration
- ❌ No comprehensive test suite
- ❌ No background job processing

These will be addressed in future phases.

## Roadmap

### Phase 1: Authentication & Users
- User registration and login
- Organization management
- Role-based access control
- Basic user profiles

### Phase 2: Core CRM
- Lead capture and qualification
- Customer database
- Opportunity management
- Basic pipeline view

### Phase 3: Task Management
- Task creation and assignment
- Follow-up tracking
- Activity logging
- Calendar integration

### Phase 4: Analytics & Reporting
- Sales dashboards
- Conversion metrics
- Team performance
- Custom reports

### Phase 5: Integrations
- WhatsApp Business API
- Email integration
- Document processing
- External insurance APIs

## Contributing

This project is currently in early development. Contribution guidelines will be established in future phases.

## License

[License to be determined]
