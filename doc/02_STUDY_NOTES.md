# FinTrack - Detailed Technical Study Notes & Architecture Guide

This document serves as a technical deep-dive for developers, examiners, and interviewers to understand the inner mechanics of the FinTrack application.

---

## 1. Frontend Architecture (React 19 + Vite)

### 1.1 Project Structure
```text
expense-tracker-frontend/
├── .env                # Local/current environment variables (VITE_API_URL)
├── .env.production     # Production build environment variables
├── vercel.json         # Single-Page-App (SPA) routing rewrite configuration
├── vite.config.js      # Vite build bundler configuration
└── src/
    ├── api/
    │   └── axios.js    # Pre-configured Axios instance with JWT interceptor
    ├── components/
    │   ├── PasswordInput.jsx  # Show/Hide password toggle component
    │   ├── PeriodFilter.jsx   # Date range & preset time window filter
    │   ├── ReportModal.jsx    # Interactive modal for PDF, Excel, and Email reports
    │   └── ThemeToggle.jsx    # Light/Dark mode switcher with localStorage persistence
    ├── pages/
    │   ├── Dashboard.jsx      # Primary dashboard: KPIs, Charts, Recent Transactions
    │   ├── AddTransaction.jsx # Form for registering income and expenses
    │   ├── Login.jsx          # 2-Step Login with 2FA OTP verification
    │   ├── Register.jsx       # User registration with instant welcome email
    │   ├── ForgotPassword.jsx # 2-Step Password Reset via email OTP
    │   ├── auth.css           # Authentication pages styling
    │   └── dashboard.css      # Dashboard layout, cards, and animations
    └── utils/
        ├── exportHelpers.js   # XLSX sheet builder and PDF canvas exporter
        └── theme.js           # Theme state getter and setter
```

### 1.2 Axios Interceptor Mechanics (`src/api/axios.js`)
* **BaseURL Dynamic Resolution:**
  ```javascript
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "https://apsarar.pythonanywhere.com/api/",
  });
  ```
  *In development*, it reads from `.env`. *In production (Vercel)*, if the `.env` file is omitted by Git, it automatically falls back to the live hosted PythonAnywhere URL.
* **JWT Request Interceptor:**
  ```javascript
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  ```
  Every outgoing HTTP request automatically checks `localStorage` for an `access` token. If found, it attaches the `Authorization: Bearer <token>` header, eliminating repetitive boilerplate across pages.

### 1.3 State Management & Hooks
FinTrack utilizes React's built-in state primitives without bloating the bundle with Redux:
* **`useState`**: Handles form inputs, modal visibility, step tracking (Step 1 vs Step 2), and loading spinners.
* **`useEffect`**: Triggers data fetching upon initial mount or when period filters change.
* **`useMemo`**: Optimizes calculation of derived data (Total Balance, Category totals, Chart datasets) so expensive filtering logic doesn't re-run unless transactions change.
* **`useRef`**: Binds to HTML DOM elements for capturing clean screenshots during PDF generation with `html2canvas`.

### 1.4 Single-Page Application (SPA) Routing on Vercel (`vercel.json`)
When React Router is deployed on static cloud hosts like Vercel, reloading on a non-root path (e.g. `/dashboard` or `/forgot-password`) results in a `404 Not Found` because the web server looks for a physical directory named `dashboard`.
FinTrack resolves this via `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```
This instructs Vercel to route all HTTP paths back to `index.html`, allowing React Router to take control client-side.

---

## 2. Backend Architecture (Django 6.0 + DRF)

### 2.1 Project Structure
```text
expense-tracker-backend/
├── backend/
│   ├── settings.py     # Global Django configurations, JWT settings, CORS, SMTP
│   ├── urls.py         # Root URL routing delegating to tracker.urls
│   └── wsgi.py         # WSGI interface for PythonAnywhere web server
├── tracker/
│   ├── email_templates.py # Responsive HTML email templates for OTP & Onboarding
│   ├── models.py       # Transaction, LoginOTP, PasswordResetOTP models
│   ├── serializers.py  # DRF ModelSerializer converting ORM models to JSON
│   ├── urls.py         # Dual-slash routes (/login/ & /login)
│   └── views.py        # Business logic, auth flows, CRUD endpoints, and Webhooks
└── manage.py           # Django command-line execution entry point
```

### 2.2 Dual-Slash Route Protection (`tracker/urls.py`)
Django's default `CommonMiddleware` enforces trailing slashes (`APPEND_SLASH = True`). When an HTTP POST request is sent to `/api/login` (without slash), Django cannot redirect with HTTP 301 while preserving POST body data, triggering a `RuntimeError (500)`.
FinTrack uses dual routing to support both formats gracefully:
```python
path('login/', login_user),
path('login', login_user),
path('register/', register_user),
path('register', register_user),
```

### 2.3 CORS (Cross-Origin Resource Sharing)
Since the frontend runs on `http://localhost:5173` or `https://*.vercel.app` while the backend runs on `https://apsarar.pythonanywhere.com`, browsers enforce the Same-Origin Policy.
FinTrack implements `corsheaders.middleware.CorsMiddleware` placed at the top of Django middleware with:
```python
CORS_ALLOW_ALL_ORIGINS = True
```
This returns the headers `access-control-allow-origin: *` and `access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS` on pre-flight `OPTIONS` requests, preventing browser CORS blocks.

---

## 3. Database Schema & Models

### 3.1 Entity Relationship Diagram (ERD)

```
       +-------------------------+
       |   django.contrib.auth   |
       |          User           |
       +-------------------------+
       | PK  id (Integer)        |
       |     username (VarChar)  |
       |     email (VarChar)     |
       |     password (Hash)     |
       +------------+------------+
                    | 1
                    |
      +-------------+-------------+
      | 1                         | 1
      |                           |
      v *                         v *
+--------------------+      +--------------------+
|    Transaction     |      |      LoginOTP      |
+--------------------+      +--------------------+
| PK id              |      | PK id              |
| FK user_id         |      | FK user_id         |
|    title (VarChar) |      |    otp (6-digits)  |
|    amount (Float)  |      |    created_at      |
|    type (inc/exp)  |      |    is_used (Bool)  |
|    date (DateTime) |      +--------------------+
+--------------------+
```

### 3.2 Model Specifications:
* **`Transaction`:** Stores user-owned income and expense records. Cascade deletion ensures all records are purged when an account is deleted.
* **`LoginOTP`:**
  * Stores temporary 6-digit verification codes generated during login.
  * `generate_otp_for_user(user)`: Invalidates all older unused OTPs for the user before issuing a fresh code.
  * `is_valid()`: Enforces a strict **10-minute Time-To-Live (TTL)**:
    ```python
    def is_valid(self):
        if self.is_used:
            return False
        return (timezone.now() - self.created_at) <= datetime.timedelta(minutes=10)
    ```
* **`PasswordResetOTP`:** Same TTL and invalidation logic specifically scoped for forgotten password workflows.

---

## 4. Authentication, Security & OTP Mechanics

### 4.1 Login 2-Factor Authentication (2FA) Protocol
1. **Step 1 (Credential Verification):**
   * Client posts `{ username, password }` to `/api/login/`.
   * Server validates user presence and executes `django.contrib.auth.authenticate()`.
   * If credentials are valid, the server calls `LoginOTP.generate_otp_for_user(user)` to create a random 6-digit code.
   * Server dispatches the HTML-styled verification email via Google SMTP.
   * Returns `{ otp_required: true, username: "...", email: "sa***@gmail.com" }`. No tokens are issued at this stage.
2. **Step 2 (OTP Verification):**
   * Client receives OTP input from the user and posts `{ username, otp }` to `/api/login/verify-otp/`.
   * Server queries the newest unused OTP for that user.
   * Server verifies:
     * Does the OTP match?
     * Is `is_used == False`?
     * Has fewer than 10 minutes elapsed since `created_at`?
   * If valid, server marks `otp.is_used = True` (preventing replay attacks) and issues standard SimpleJWT `access` and `refresh` tokens.

### 4.2 Security Best Practices Implemented:
* **Password Hashing:** Passwords are never stored in plaintext. Django uses **PBKDF2 with a SHA256 hash** and salt.
* **Replay Attack Prevention:** Once an OTP is verified, `is_used` is set to `True`. Subsequent attempts with the same code will fail.
* **Email Obfuscation:** The server masks recipient emails (e.g. `sa***@gmail.com`) so sensitive account information isn't exposed in responses.
* **Input Coercion:** All incoming data fields are explicitly coerced to string and stripped (`str(val).strip()`) to prevent type errors or non-string payload injection crashes.

---

## 5. Email Notification & SMTP Architecture

### 5.1 PythonAnywhere Networking & Gmail Whitelist
On free cloud hosting tiers (like PythonAnywhere Beginner accounts), general outbound socket connections (like port 25 or arbitrary SMTP hosts) are blocked.
However, PythonAnywhere explicitly **whitelists Gmail's SMTP server (`smtp.gmail.com:587`)**.

### 5.2 Google App Passwords
Due to Google's sunsetting of "Less Secure Apps", standard Gmail passwords cannot be used for programmatic SMTP authentication when 2-Step Verification is active.
FinTrack utilizes a dedicated **16-character Google App Password** configured in `.env` and `settings.py`:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apsaraappdevelopment@gmail.com'
EMAIL_HOST_PASSWORD = 'hdrnydnfkqxtxddw'
```

### 5.3 Responsive HTML Email Templates (`tracker/email_templates.py`)
Rather than sending plain text emails, FinTrack builds rich HTML emails featuring:
* Table-based layout ensuring 100% rendering fidelity across Gmail Mobile App, Apple Mail, and Outlook.
* Gradient brand banner with `FinTrack` typography and Diamond badge.
* Large, monospace letter-spaced 6-digit OTP code box (`letter-spacing: 8px`).
* Security warning box warning users never to disclose their code.

---

## 6. Continuous Deployment (CI/CD) Webhook

FinTrack backend implements an automated deployment webhook at `/api/deploy/`.
* **Security:** Verifies GitHub's `X-Hub-Signature-256` HMAC secret or manual `?token=` parameter.
* **Execution:**
  1. Executes `git pull` inside the server directory.
  2. Runs `python manage.py migrate` to apply any new database schema migrations.
  3. Touches the PythonAnywhere WSGI file (`/var/www/apsarar_pythonanywhere_com_wsgi.py`), which immediately triggers PythonAnywhere's uWSGI master process to restart worker threads without downtime.
