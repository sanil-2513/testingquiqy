# Git and GitHub workflow – commit-by-commit

This workflow keeps the original member responsibilities visible while producing one integrated application. The current project already contains the combined modules; use the commits below to explain the intended development history and to guide your actual team branches. **Do not fabricate old commits or claim that a branch was independently developed if it was not.** If the four members already have separate repositories, add each member's code through reviewed Pull Requests.

## 1. Publish the prepared Git repository

This project archive already includes a Git repository with `main`, `develop`, four feature branches, merge commits and the `v1.0.0` tag. Create an **empty** GitHub repository named `GoodBite-Restaurant-Ordering-System` (do not initialize it with a README or license). From this project folder:

```bash
git remote add origin https://github.com/YOUR-USERNAME/GoodBite-Restaurant-Ordering-System.git
git push -u origin main
git push -u origin develop
git push origin --all
git push origin --tags
```

This publishes the existing branch and commit history. Do not run `git init` again.

## 2. Create the integration branch

```bash
git switch -c develop
git push -u origin develop
```

## 3. Member feature branches

For each member, create a branch from the latest `develop`, make that member's scoped changes, test, push and open a Pull Request into `develop`.

```bash
git switch develop
git pull origin develop
git switch -c feature/auth-menu
# Work only on authentication/menu files
git add goodbite/auth_menu goodbite/database.py
git commit -m "feat(auth-menu): add account and menu management"
git push -u origin feature/auth-menu
```

Repeat with:
- `feature/cart-customization` – `goodbite/cart_customization/`
- `feature/checkout-payment` – `goodbite/checkout_payment/`
- `feature/orders-delivery` – `goodbite/orders_delivery/`

Each PR should include a short description, screenshots, test results and reviewer approval. Merge the PR into `develop` using GitHub's **Create a merge commit** option if you want the merge visible in history. Pull the updated `develop` before starting the next feature branch.

## 4. Integration branch work

```bash
git switch develop
git pull origin develop
git switch -c feature/integration-ui
```

Connect the modules through `app.py`: menu items become cart items, cart totals go to checkout, successful simulated payment creates a persisted order, and order state changes publish notifications.

```bash
git add app.py templates goodbite/database.py
git commit -m "feat(integration): connect menu cart checkout and orders"
git push -u origin feature/integration-ui
```

Open a PR into `develop`, review it, run tests, then merge.

## 5. Tests and bug fixes

```bash
git switch develop
git pull origin develop
pytest -q
git switch -c bugfix/checkout-order-validation
# Make and test a specific correction
git add .
git commit -m "fix(checkout): validate order and delivery details"
git push -u origin bugfix/checkout-order-validation
```

Open a PR into `develop`. Keep bug fixes as separate commits instead of silently changing files.

## 6. Release

After the full application has been tested:

```bash
git switch main
git pull origin main
git merge --no-ff develop -m "release: merge integrated GoodBite application"
git tag -a v1.0.0 -m "GoodBite v1.0.0"
git push origin main --tags
```

If you use GitHub Pull Requests for the release, open a PR from `develop` into `main` and create the tag after merging.

## 7. Demonstrate the history

```bash
git log --oneline --graph --decorate --all
git branch -a
git status
```

A good submission shows meaningful feature commits, reviewable PRs, test/fix commits, merge commits and a release tag. Never create artificial conflict commits just to make the graph look busy.
