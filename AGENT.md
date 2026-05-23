# DrGame Agent Notes

## Understanding
- DrGame is a multi-branch ERP and e-commerce platform for gaming products, physical games, digital accounts, repairs, procurement, accounting, HR, CRM, notifications, documents, and assets.
- The architecture requires a monorepo with a Django 5 + DRF backend, Next.js 14 frontend, Redis for Channels/Celery, an external PostgreSQL database via `DATABASE_URL`, and Nginx as reverse proxy.
- Authentication is OTP-only by phone number; passwords are not part of the product model. JWT is used after OTP verification.
- Branch stock is independent for physical goods, while digital game-account inventory is central/shared across all branches.
- Phase order matters: backend foundations come first, frontend integration follows after API contracts are in place.

## Current Progress
- Completed Phase 1.1 environment and project setup.
- Added backend scaffold under `backend/` with Django settings split into `base.py`, `development.py`, and `production.py`.
- Added backend support files for ASGI/Channels, a WebSocket health consumer, Celery, HTTP health endpoint, installed apps, service placeholders for SMS, OTP, and payment.
- Added empty Django app packages for all modules listed in `architecture.md` so future phases have stable import paths.
- Added frontend scaffold under `frontend/` with Next.js App Router, TypeScript, Tailwind config, auth store, Axios client, WebSocket reconnect client, and initial public/auth/panel layouts.
- Filled Docker Compose, development override, Nginx reverse proxy, `.env.example`, and Makefile for common development commands.
- Implemented Phase 1.2 backend Core foundation: custom phone-based `User`, `OTPCode`, `Branch`, RBAC (`Role`, `Module`, `Permission`, `UserRole`), `AuditLog`, admin registrations, migrations, and seed data for default modules/roles.
- Implemented Phase 1.2 backend APIs under `/api/v1/`: OTP request/verify, JWT refresh/logout, current user, current roles, Branch CRUD, Role CRUD, role permission matrix updates, and read-only audit logs.

## Phase 1.1 Status
- Backend monorepo structure: done.
- Docker Compose services for nginx, backend, celery, celery-beat, frontend, redis: done.
- Django project/settings structure: done.
- DRF, CORS, Channels, Celery, Redis configuration: scaffolded.
- Nginx reverse proxy for `/api/v1/`, `/ws/`, `/admin/`, and frontend root: done.
- Frontend project scaffold with TypeScript/App Router/Tailwind: done.
- Axios JWT interceptor, Zustand auth store, WebSocket client, base layouts: scaffolded.

## Phase 1.2 Status
- Custom `User` with phone as `USERNAME_FIELD`: done.
- `OTPCode` with expiration, attempts, verification, and SMS placeholder integration: done.
- SimpleJWT login flow via OTP verification: done.
- Auth APIs: `POST /auth/request-otp/`, `POST /auth/verify-otp/`, `POST /auth/token/refresh/`, `POST /auth/logout/`, `GET/PATCH /auth/me/`, `GET /auth/me/roles/`: done.
- RBAC models and seeded default roles/modules: done.
- Role and role-permission admin APIs: done.
- `Branch` model and CRUD API: done.
- `AuditLog` model, read API, and middleware-based request logging: scaffolded.
- Frontend Phase 1.2 auth pages, token cookie strategy, protected route guard, profile page, and role switcher are still pending.
- Runtime migration/API verification is pending because Python dependencies are not installed locally in this workspace.

## Next Development Step
- Finish the Phase 1.2 frontend authentication flow: OTP login page, token persistence/refresh behavior, protected panel guard, user profile page, and role switcher UI wired to the new Core APIs.
- After dependencies are installed, run backend validation with `python backend/manage.py check`, `python backend/manage.py migrate`, and API smoke tests for `/api/v1/auth/*`, `/api/v1/branches/`, and `/api/v1/roles/`.

## Local Run Notes
- Docker Hub image pulls are routed through Arvan by default using `DOCKER_REGISTRY=docker.arvancloud.ir` and `DOCKER_OFFICIAL_NAMESPACE=library`.
- Backend and frontend Dockerfiles accept mirror build args, so the mirror can be changed without editing source files.
- `PIP_INDEX_URL` and `NPM_REGISTRY` are configurable in `.env.example`; they currently default to official registries because Arvan is only being used for Docker image pulls.
