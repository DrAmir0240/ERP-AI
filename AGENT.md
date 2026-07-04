# DrGame Agent Notes

## Understanding
- DrGame is a multi-branch ERP and e-commerce platform for gaming products, physical games, digital accounts, repairs, procurement, accounting, HR, CRM, notifications, documents, and assets.
- The architecture requires a monorepo with a Django 5 + DRF backend, Next.js 14 frontend, Redis for Channels/Celery, an external PostgreSQL database via `DATABASE_URL`, and Nginx as reverse proxy.
- Authentication is OTP-only by phone number; passwords are not part of the product model. JWT is used after OTP verification.
- Branch stock is independent for physical goods, while digital game-account inventory is central/shared across all branches.
- Phase order matters: backend foundations come first, frontend integration follows after API contracts are in place.

## Current Progress
- Completed Phase 1.1 environment and project setup.
- Completed Phase 1.2 authentication, RBAC, and Core admin.
- Completed Phase 2.1 inventory: Category, Product, StockItem, StockMovement, BranchTransfer models, serializers, views, signals, admin, frontend API/types/UI.
- Completed Phase 2.2 accounts management: GameAccount, Game, AccountGame, AccountSale models, signals, serializers, views, URLs, admin, frontend API/types/UI.
- Completed Phase 3.1 orders: Order, OrderItem models, serializers, views, URLs, admin, frontend types/API/UI.
- Completed Phase 3.2 invoice & payment: Invoice, Payment, Refund, ReturnPolicy models, serializers, views, frontend types/API/UI.
- Completed Phase 4.1 repair: RepairOrder, RepairSettings models, serializers, views, URLs, admin, frontend types/API/UI.
- Completed Phase 4.2 procurement: Supplier, PurchaseRequest, PurchaseOrder models, serializers, views, URLs, admin, frontend types/API/UI.

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

## Phase 2.1 Status — Inventory
- `Category` (3-level self-referential), `Product`, `StockItem`, `StockMovement`, `BranchTransfer` models: done.
- Serializers: CategorySerializer, ProductSerializer, StockItemSerializer, BulkStockItemSerializer, StockStatusUpdateSerializer, StockMovementSerializer, BranchTransferSerializer, BranchTransferStatusSerializer: done.
- ViewSets: CategoryViewSet, ProductViewSet, StockItemViewSet, StockMovementViewSet, BranchTransferViewSet: done.
- Signals: auto StockMovement creation on StockItem save: done.
- Admin registrations: done.
- URLs: `api/v1/inventory/categories/`, `products/`, `stock/`, `movements/`, `transfers/`: done.
- Frontend: TypeScript types, 17 API functions, InventoryManager component (tabs: products, categories, stock, movements, transfers): done.

## Phase 2.2 Status — Accounts Management
- `GameAccount` model (PS online/offline, Xbox, Nintendo) with `total_capacity`, `sold_count`: done.
- `Game` model with platform choices (ps, xbox, nintendo): done.
- `AccountGame` M2M junction table with unique constraint: done.
- `AccountSale` model with order_id, customer FK, sold_games JSONField: done.
- Signal: auto-increment `sold_count` on AccountSale create, auto-decrement on delete: done.
- Serializers: GameSerializer, GameAccountSerializer (with game_ids write-only for M2M management), GameAccountListSerializer (with game_count annotation), AccountSaleSerializer, CalculatePriceSerializer: done.
- ViewSets: GameViewSet (IsAdminOrReadOnly), GameAccountViewSet (IsEmployee, list/detail serializer split, sales action), AccountSaleViewSet (IsEmployee), CalculatePriceView (IsEmployee): done.
- Admin: GameAccountAdmin, GameAdmin, AccountGameAdmin, AccountSaleAdmin: done.
- URLs: `api/v1/accounts/games/`, `ps/`, `ps/{id}/sales/`, `sales/`, `calculate-price/`: done.
- Migration: `0001_initial.py` hand-written (depends on core 0003): done.
- Frontend types: AccountType, GamePlatform, Game, GameAccountGame, GameAccount, GameAccountListItem, AccountSale, CalculatePriceResult, GameAccountInput, GameInput: done.
- Frontend API: listGames, createGame, updateGame, deleteGame, listGameAccounts, getGameAccount, createGameAccount, updateGameAccount, deleteGameAccount, listAccountSales, listAllSales, createAccountSale, calculatePrice: done.
- Frontend AccountsManager component (tabs: accounts, games, sales log, calculator): done.
- Admin panel page at `/admin/accounts` with PanelShell: done.
- Admin dashboard updated with accounts link: done.
- **Pending**: Run `python backend/manage.py makemigrations --check --dry-run` and frontend typecheck/lint to validate (classifier was unavailable during implementation).

## Next Development Step
- Move to Phase 5.1: Accounting — Chart of Accounts, JournalEntry, JournalLine, TaxConfig, ExpenseIncomeCategory models and APIs.
- Journal Entry auto-creation for orders, payments, repairs, and procurement (currently placeholder/deferred to Phase 5).
- Before starting Phase 5: validate all Phase 3 & 4 migrations and frontend build.

## Phase 3.1 Status — Orders
- `Order` model with auto-generated order_number (ORD-YYMM-NNNNN), order_type, channel, branch, customer, cashier, 8-state status workflow, subtotal/discount/tax/total, payment_status, courier fields: done.
- `OrderItem` model with item_type (product/game_account/game/repair), FKs to product/stock_item/account, game_ids JSON: done.
- Serializers: OrderItemSerializer, OrderSerializer (detail), OrderListSerializer (with item_count), CreateOrderSerializer (@transaction.atomic, marks stock as sold), OrderStatusSerializer, OrderCourierSerializer, CancelOrderSerializer (rolls back stock): done.
- `OrderViewSet` with full CRUD + @action for status, courier, cancel, invoice, payments, refund: done.
- Admin: OrderAdmin with OrderItemInline, InvoiceAdmin, PaymentAdmin, RefundAdmin, ReturnPolicyAdmin: done.
- URLs: `api/v1/orders/orders/`, `refunds/`, `return-policies/`: done.
- Frontend types: OrderType, OrderChannel, OrderStatus, PaymentStatus, PaymentMethod, etc. (12 types): done.
- Frontend API: listOrders, getOrder, createOrder, updateOrderStatus, updateOrderCourier, cancelOrder, getInvoice, listPayments, createPayment, requestRefund, listRefunds, approveRefund, rejectRefund, listReturnPolicies, createReturnPolicy, updateReturnPolicy: done.
- Frontend OrdersManager component (tabs: orders, refunds) with order detail view, payment form, status change: done.
- Admin panel page at `/admin/orders`: done.

## Phase 3.2 Status — Invoice & Payment
- `Invoice` model with auto-generated invoice_number (INV-YYMM-NNNNN), OneToOne to Order, tax_rate/tax_amount/total/pdf_url: done.
- `Payment` model with method choices (online/wallet/cash/pos), status workflow, reference_code, paid_by FK: done.
- `Refund` model with status workflow (pending/approved/rejected/completed), refund_method: done.
- `ReturnPolicy` model with category OneToOne, return_days, is_returnable: done.
- PaymentSerializer with auto payment_status update on order: done.
- RefundSerializer, RefundActionSerializer (approve/reject/complete): done.
- RefundViewSet (ReadOnly + approve/reject actions): done.
- ReturnPolicyViewSet (IsAdminOrReadOnly): done.
- **Deferred**: VAT calculation from TaxConfig, PDF generation, initiate_payment placeholder, Journal Entry auto-creation (Phase 5).

## Phase 4.1 Status — Repair
- `RepairSettings` model with markup_percent (default 20%), updated_by, get_markup() classmethod: done.
- `RepairOrder` model with 11-state status workflow, OneToOne to Order, device_type/model, technician FK, technician_price, auto markup_percent, calculated final_price, customer_approved NullBoolean: done.
- Serializers: RepairSettingsSerializer (update_or_create), RepairOrderSerializer, RepairAcceptSerializer, RepairPriceSerializer (auto markup), CustomerDecisionSerializer, RepairCompleteSerializer, RepairStatusSerializer: done.
- RepairOrderViewSet with accept, price, customer-decision, complete, status actions: done.
- RepairSettingsViewSet with auto-create singleton on list: done.
- URLs: `api/v1/repair/orders/`, `settings/`: done.
- Frontend types, API (9 functions), RepairManager component (tabs: repairs, settings): done.
- Admin panel page at `/admin/repair`: done.
- **Deferred**: Journal Entry for repair income/technician fee (Phase 5).

## Phase 4.2 Status — Procurement
- `Supplier` model with company_name, contact_person, phone, email, address, balance, notes, is_active: done.
- `PurchaseRequest` model with auto request_number (PR-YYMM-NNNNN), status workflow (draft/submitted/approved/rejected/purchased), requested_by, approved_by, items JSON: done.
- `PurchaseOrder` model with auto purchase_number (PO-YYMM-NNNNN), supplier FK, request FK (optional), items JSON, total_amount, payment_method, supplier_invoice_no, purchased_by: done.
- CreatePurchaseOrderSerializer: @transaction.atomic, auto-marks linked PurchaseRequest as purchased, creates StockMovement for each item: done.
- SupplierViewSet with list annotated order_count, PurchaseRequestViewSet with status action, PurchaseOrderViewSet: done.
- URLs: `api/v1/procurement/suppliers/`, `requests/`, `orders/`: done.
- Frontend types, API (11 functions), ProcurementManager component (tabs: suppliers, requests, purchase-orders): done.
- Admin panel page at `/admin/procurement`: done.
- Admin dashboard updated with orders, repair, procurement links: done.
- **Deferred**: Journal Entry for purchases (Phase 5).

## Migrations — Phase 3 & 4
- `orders/migrations/0001_initial.py`: hand-written, depends on core 0003, inventory 0001, accounts 0001.
- `repair/migrations/0001_initial.py`: hand-written, depends on orders 0001.
- `procurement/migrations/0001_initial.py`: hand-written, depends on core 0003.
- All three apps include `migrations/__init__.py`.
- URL wiring: `api/v1/orders/`, `api/v1/repair/`, `api/v1/procurement/` added to `config/urls.py`.
- **Pending**: Run `python manage.py makemigrations --check` and frontend typecheck/lint to validate.

## Remaining Blockers / Warnings
- Initial `npm install` failed against the project mirror with `npm ERR! request to https://npm.devneeds.ir/@hookform%2fresolvers failed, reason: getaddrinfo EAI_AGAIN npm.devneeds.ir`; retrying with `--registry=https://registry.npmjs.org/` succeeded.
- Plain `npm run lint` cannot write cache while `frontend/.next` is root-owned: `EACCES: permission denied, mkdir '/home/doki/Desktop/Projects/DrGame/frontend/.next/cache/eslint'`; `npm run lint -- --no-cache` passes.
- `sudo chown -R doki:doki /home/doki/Desktop/Projects/DrGame/frontend/.next` could not run non-interactively: `sudo: a terminal is required to read the password`.
- `check --deploy` reports expected development security warnings: `security.W004`, `security.W008`, `security.W009`, `security.W012`, `security.W016`, and `security.W018`.
- Migration for accounts was hand-written because the Django classifier was unavailable; regenerate with `python backend/manage.py makemigrations accounts` if there's a mismatch.

## Local Run Notes
- Docker Hub image pulls are routed through Arvan by default using `DOCKER_REGISTRY=docker.arvancloud.ir` and `DOCKER_OFFICIAL_NAMESPACE=library`.
- Backend and frontend Dockerfiles accept mirror build args, so the mirror can be changed without editing source files.
- `PIP_INDEX_URL` and `NPM_REGISTRY` are configurable in `.env.example`; they currently default to official registries because Arvan is only being used for Docker image pulls.
