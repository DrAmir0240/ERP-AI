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
- Added backend support files for ASGI/Channels, a WebSocket health consumer, Celery, HTTP health endpoint, installed apps, SMS/OTP adapter stubs, and a deterministic development payment adapter.
- Added empty Django app packages for all modules listed in `architecture.md` so future phases have stable import paths.
- Added frontend scaffold under `frontend/` with Next.js App Router, TypeScript, Tailwind config, auth store, Axios client, WebSocket reconnect client, and initial public/auth/panel layouts.
- Filled Docker Compose, development override, Nginx reverse proxy, `.env.example`, and Makefile for common development commands.
- Implemented Phase 1.2 backend Core foundation: custom phone-based `User`, `OTPCode`, `Branch`, RBAC (`Role`, `Module`, `Permission`, `UserRole`), `AuditLog`, admin registrations, migrations, and seed data for default modules/roles.
- Implemented Phase 1.2 backend APIs under `/api/v1/`: OTP request/verify, JWT refresh/logout, current user, current roles, Branch CRUD, Role CRUD, role permission matrix updates, and read-only audit logs.
- Implemented Phase 1.2 backend permission classes: `IsAdmin`, `IsEmployee`, `IsBranchMember`, and `IsAdminOrReadOnly`.
- Implemented Phase 1.2 frontend authentication and Core admin flow: OTP login form, persisted JWT session store, automatic access-token refresh, protected panel route guard, profile page, logout action, role switcher UI, Branch CRUD page, and Role permission matrix page.

## Phase 1.1 Status
- Backend monorepo structure: done.
- Docker Compose services for nginx, backend, celery, celery-beat, frontend, redis: done.
- Django project/settings structure: done.
- DRF, CORS, Channels, Celery, Redis configuration: done.
- Nginx reverse proxy for `/api/v1/`, `/ws/`, `/admin/`, and frontend root: done.
- Frontend project scaffold with TypeScript/App Router/Tailwind: done.
- Axios JWT interceptor with refresh retry, Zustand persisted auth store, WebSocket client, and base layouts: done.

## Phase 1.2 Status
- Custom `User` with phone as `USERNAME_FIELD`: done.
- `OTPCode` with expiration, attempts, verification, and SMS adapter integration: done.
- SimpleJWT login flow via OTP verification: done.
- Auth APIs: `POST /auth/request-otp/`, `POST /auth/verify-otp/`, `POST /auth/token/refresh/`, `POST /auth/logout/`, `GET/PATCH /auth/me/`, `GET /auth/me/roles/`: done.
- RBAC models and seeded default roles/modules: done.
- Role and role-permission admin APIs: done.
- `Branch` model and CRUD API: done.
- `AuditLog` model, read API, and middleware-based request logging wired in `MIDDLEWARE`: done.
- Frontend Phase 1.2 auth pages, persisted token strategy, protected route guard, profile page, logout, role switcher UI, Branch CRUD page, and Role permission matrix page: done.
- Migration consistency verified with `python backend/manage.py makemigrations --check --dry-run`: passed (`No changes detected`).
- Backend deploy check ran with `python backend/manage.py check --deploy 2>&1 | head -60`: passed with security warnings only.
- Frontend validation ran with `npm install --registry=https://registry.npmjs.org/`, `npm run typecheck`, and `npm run lint -- --no-cache`: passed.

## Next Development Step
- Move to Phase 2.1 inventory foundations: product/category/stock models, branch stock APIs, stock movement logging, and inventory admin UI.
- Before production deployment, set real production security values and rerun `python backend/manage.py check --deploy`.

## Remaining Blockers / Warnings
- Initial `npm install` failed against the project mirror with `npm ERR! request to https://npm.devneeds.ir/@hookform%2fresolvers failed, reason: getaddrinfo EAI_AGAIN npm.devneeds.ir`; retrying with `--registry=https://registry.npmjs.org/` succeeded.
- Plain `npm run lint` cannot write cache while `frontend/.next` is root-owned: `EACCES: permission denied, mkdir '/home/doki/Desktop/Projects/DrGame/frontend/.next/cache/eslint'`; `npm run lint -- --no-cache` passes.
- `sudo chown -R doki:doki /home/doki/Desktop/Projects/DrGame/frontend/.next` could not run non-interactively: `sudo: a terminal is required to read the password`.
- `check --deploy` reports expected development security warnings: `security.W004`, `security.W008`, `security.W009`, `security.W012`, `security.W016`, and `security.W018`.

## Local Run Notes
- Docker Hub image pulls are routed through Arvan by default using `DOCKER_REGISTRY=docker.arvancloud.ir` and `DOCKER_OFFICIAL_NAMESPACE=library`.
- Backend and frontend Dockerfiles accept mirror build args, so the mirror can be changed without editing source files.
- `PIP_INDEX_URL` and `NPM_REGISTRY` are configurable in `.env.example`; they currently default to official registries because Arvan is only being used for Docker image pulls.
