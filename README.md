# GoodBite – Restaurant Ordering System

A single Flask application combining the four independently developed coursework modules. It preserves all ten allocated design patterns and connects the complete customer journey.

## Features

- Register, log in and log out; password hashes are stored, not plain-text passwords.
- Restaurant menu with administrator-only menu management.
- Cart with add-ons, quantity changes, removal and meal-combo builder.
- Checkout with discount strategies and simulated Card / UPI / Wallet adapters.
- Order creation, order history, delivery status tracking and observer notifications.
- Admin can advance order status and manage menu items.

## Design patterns preserved

| Member module | Design pattern | Implementation |
|---|---|---|
| Authentication & Menu | Singleton | `goodbite/database.py` – `DatabaseManager` |
| Authentication & Menu | Factory Method | `goodbite/auth_menu/menu_factory.py` |
| Authentication & Menu | Proxy | `goodbite/auth_menu/menu_proxy.py` |
| Cart & Customization | Command | `goodbite/cart_customization/commands.py` |
| Cart & Customization | Decorator | `goodbite/cart_customization/decorators.py` |
| Cart & Customization | Builder | `goodbite/cart_customization/meal_builder.py` |
| Checkout & Payment | Strategy | `goodbite/checkout_payment/discounts.py` |
| Checkout & Payment | Adapter | `goodbite/checkout_payment/payment_adapters.py` |
| Checkout & Payment | Facade | `goodbite/checkout_payment/checkout_facade.py` |
| Orders & Delivery | Observer | `goodbite/orders_delivery/observers.py` |
| Orders & Delivery | State | `goodbite/orders_delivery/order_states.py` |

## Run locally (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

The local default database is `goodbite.db` (SQLite). It is created automatically on first request.

Demo administrator:
- Email: `admin@goodbite.local`
- Password: `Admin123!`

Change the admin password for any shared/demo environment using the `ADMIN_PASSWORD` environment variable before the first database initialization. For deployment, also set a long random `SECRET_KEY`.

## Test

```powershell
pytest -q
```

## Deploy to Vercel

**Important:** Vercel's function filesystem is ephemeral. Do not use the local SQLite file as a production database. Create a managed PostgreSQL database (for example, Neon or Supabase) and configure its connection string as a Vercel environment variable.

1. Push this project to a GitHub repository.
2. Create a managed PostgreSQL database and copy its connection string. Ensure SSL is enabled if required by the provider.
3. In Vercel, choose **Add New → Project**, import the GitHub repository.
4. Keep the project root as the repository root. Vercel detects the Flask app from `app.py` and installs dependencies from `requirements.txt`.
5. In **Project → Settings → Environment Variables**, add:
   - `DATABASE_URL` = PostgreSQL connection string
   - `SECRET_KEY` = long random secret
   - `ADMIN_PASSWORD` = strong administrator password
6. Add the variables for Production (and Preview if you intend to use preview deployments).
7. Deploy. The app initializes the schema and seed menu on first request.
8. Test registration, login, cart, checkout and order tracking on the deployed URL.

Vercel automatically detects the root-level Flask app in `app.py` and installs packages from `requirements.txt`; custom routing configuration is not required. Python 3.12 is pinned in `.python-version`.

Payment adapters in this academic project are simulations. They do not charge real cards, UPI accounts or wallets. Email notifications are console simulations. Do not collect real payment credentials.

## Git workflow for coursework demonstration

Suggested workflow:
- `main`: stable release
- `develop`: integration branch
- `feature/auth-menu`
- `feature/cart-customization`
- `feature/checkout-payment`
- `feature/orders-delivery`
- `feature/integration-ui`
- `bugfix/...` for fixes

Make small commits with meaningful messages. Merge feature branches into `develop` using Pull Requests after reviewing changes and running tests. Merge `develop` into `main` only after the complete flow passes. This downloadable project includes a prepared `.git` history with feature branches, merge commits and a `v1.0.0` tag. Publish it using the commands in `GIT_WORKFLOW.md`; do not re-run `git init`. See that file for the commit-by-commit process.
