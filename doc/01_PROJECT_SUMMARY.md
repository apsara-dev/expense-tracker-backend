# FinTrack - Full-Stack Wealth & Expense Management Platform

## 1. Project Overview
**FinTrack** is a modern, production-ready Full-Stack Personal Finance and Wealth Management web application. It empowers users to monitor their personal cash flow, set monthly target budgets, analyze financial health with interactive visual charts, export comprehensive reports (Excel & PDF), and secure their financial accounts with Two-Factor Authentication (2FA) OTP via real-time email notifications.

Built using **React 19 (Vite)** on the frontend and **Django REST Framework (DRF)** on the backend, the system demonstrates an industry-standard decoupled architecture communicating over secure, token-authenticated RESTful APIs.

---

## 2. Problem Statement & Solution

### The Problem:
Most people struggle with personal financial discipline due to:
* Lack of unified visibility into daily, monthly, and yearly cash flow.
* Absence of visual feedback on spending categories (Food, Travel, Bills, etc.).
* Vulnerability of sensitive financial data in basic single-password apps.
* Inability to export professional financial summaries for tax or personal records.

### The Solution:
FinTrack resolves these challenges through:
* **Interactive Dashboard:** Instant KPI cards displaying Total Balance, Total Income, and Total Expense with dynamic percentage cashflow calculations.
* **Smart Categorization & Analytics:** Real-time Category Breakdown Doughnut charts, Monthly Cashflow Bar charts, and Recent Transaction logs.
* **Enterprise-Grade Security:** Two-Factor Authentication (2FA) on login and password reset via automated, time-limited 6-digit OTPs delivered via SMTP.
* **Instant Exporting & Email Reporting:** Download `.xlsx` spreadsheets, printable PDFs, or dispatch automated summary statements directly to registered email addresses.

---

## 3. Core Features & Capabilities

| Module | Feature | Description |
| :--- | :--- | :--- |
| **Authentication & Security** | Two-Factor Auth (2FA) | Every login generates a secure 6-digit cryptographic OTP valid for 10 minutes, sent via Gmail SMTP. |
| | Password Reset via OTP | Self-service password recovery flow utilizing email OTP verification. |
| | JWT Token Lifecycle | Stateless session management using `access` (60m TTL) and `refresh` (24h TTL) tokens. |
| | Input Sanitization | Protection against SQL Injection, XSS, and non-string payload injection attacks. |
| **Transaction Management** | CRUD Operations | Create, Read, Update, and Delete income and expense transactions in real time. |
| | Period Filtering | Filter records by Date range, Current Month, Current Year, or All Time. |
| | Dynamic Search & Filter | Instant client-side search by title, amount, or type. |
| **Budgeting & Goals** | Monthly Target Budget | Set custom spending limits; UI dynamically computes remaining budget and warns on overspending. |
| **Data Analytics** | Chart.js Visualizations | Interactive Doughnut chart (Expense by Category) and Bar chart (Income vs Expense comparison). |
| **Export & Reporting** | Excel Export (`.xlsx`) | Generates structured spreadsheets with customized headers and transaction rows. |
| | PDF Export | Creates clean, printable statements with styling using `jsPDF` and `html2canvas`. |
| | Email Report Dispatch | Server-side financial summary compilation sent directly to recipient inbox. |
| **Backup & Disaster Recovery** | Backup Export | Download encrypted JSON snapshot containing full transaction history. |
| | Backup Restore | Upload past JSON backups with options to `merge` or `replace` existing data within atomic database transactions. |
| **Modern UX/UI** | Dark / Light Theme | Seamless theme toggle persisted in `localStorage`. |
| | Responsive Design | Fully mobile-friendly UI crafted with modern CSS glassmorphism, gradients, and micro-animations. |

---

## 4. Complete Technology Stack & Tools

### **Frontend:**
* **Core Framework:** React 19 (Functional Components with Hooks: `useState`, `useEffect`, `useMemo`, `useRef`).
* **Build Tool:** Vite 8 (Hot Module Replacement, fast bundling, and environment variable support).
* **Routing:** React Router DOM v7 (Client-side route protection, redirects, and SPA navigation).
* **HTTP Client:** Axios (Configured with request interceptors for JWT Bearer tokens and dynamic environment baseURLs).
* **Data Visualization:** Chart.js & React-ChartJS-2 (Interactive canvas-rendered charts).
* **Document Generation:** `xlsx` (SheetJS) for Excel workbooks; `jspdf` & `html2canvas` for PDF generation.
* **Styling:** Custom Vanilla CSS with Design System variables, Glassmorphism, and Tailwind CSS PostCSS integration.

### **Backend:**
* **Language & Runtime:** Python 3.10+ / 3.13.
* **Framework:** Django 5.x / 6.0 with Django REST Framework (DRF).
* **Authentication:** `djangorestframework-simplejwt` (JSON Web Tokens).
* **Cross-Origin Security:** `django-cors-headers` (Configured for unrestricted origins across Vercel and local dev).
* **Email System:** Django Core Mail with `smtp.gmail.com:587` (TLS) and custom responsive HTML email templates.
* **Database:** SQLite3 (Local development and PythonAnywhere lightweight production deployment).
* **CI/CD Webhook:** Custom HMAC-SHA256 authenticated webhook endpoint triggering auto `git pull`, migration, and WSGI reload on code push.

### **Cloud Infrastructure & Hosting:**
* **Frontend Hosting:** Vercel (Auto-deploy on GitHub push, SPA rewrites enabled via `vercel.json`).
* **Backend Hosting:** PythonAnywhere Cloud (Hosted WSGI application at `https://apsarar.pythonanywhere.com/api/`).
* **Source Control:** GitHub (`apsara-dev/expense-tracker-frontend` & `apsara-dev/expense-tracker-backend`).

---

## 5. System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT (BROWSER)                                 |
|                                                                                   |
|  [ React 19 SPA (Vite) ]                                                          |
|   |-- Pages: Login (2FA), Register, ForgotPassword, Dashboard, AddTransaction     |
|   |-- Components: ThemeToggle, PasswordInput, PeriodFilter, ReportModal           |
|   +-- Axios Client (Bearer Token Interceptor, BaseURL: PythonAnywhere / Local)   |
+------------------------------------------+----------------------------------------+
                                           |
                                 HTTPS REST API Requests
                                 (JSON Payloads + JWT)
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        HOSTED BACKEND (PythonAnywhere / Django)                   |
|                                                                                   |
|  [ WSGI Application ]                                                             |
|   |-- Middleware: CorsMiddleware, SecurityMiddleware, CommonMiddleware            |
|   |-- SimpleJWT: JWT Authentication Filter & Token Verification                   |
|   |-- URL Routing (/api/login/, /api/register/, /api/transactions/, etc.)         |
|   |-- View Logic: tracker.views (DRF APIViews & Generics)                         |
|   |-- Business Logic: 2FA OTP Generation, 10-min TTL Check, Transaction CRUD     |
|   |-- Email Engine: Responsive HTML Templates -> Google SMTP (smtp.gmail.com:587)  |
|   +-- CI/CD Webhook: GitHub Push -> Auto Pull -> Migrate -> WSGI Reload           |
+------------------------------------------+----------------------------------------+
                                           |
                                    ORM Queries (SQL)
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                              DATABASE (SQLite3)                                   |
|                                                                                   |
|  [ auth_user ]            [ tracker_transaction ]    [ tracker_loginotp ]         |
|  - id, username, email    - id, user_id, title       - id, user_id, otp           |
|  - password (PBKDF2)      - amount, type, date       - created_at, is_used        |
+-----------------------------------------------------------------------------------+
```

---

## 6. End-to-End User Authentication Flow

```
[ User ]                      [ Frontend ]                     [ Backend ]               [ Gmail SMTP ]
   |                               |                                |                          |
   |-- 1. Enter User & Pass ------>|                                |                          |
   |                               |-- 2. POST /api/login/ -------->|                          |
   |                               |                                |-- 3. Verify Password     |
   |                               |                                |-- 4. Generate 6-digit OTP|
   |                               |                                |-- 5. Send Email -------->|
   |                               |                                |                          |-- 6. Deliver OTP to Inbox
   |                               |<-- 7. { otp_required: true } --|                          |
   |<-- 8. Show OTP Input Screen --|                                |                          |
   |                               |                                |                          |
   |-- 9. Check Gmail for Code --->|                                |                          |
   |-- 10. Enter 6-Digit OTP ----->|                                |                          |
   |                               |-- 11. POST /api/verify-otp/ -->|                          |
   |                               |                                |-- 12. Validate OTP & TTL |
   |                               |<-- 13. { access, refresh } ----|                          |
   |<-- 14. Open Dashboard Screen -|                                |                          |
```
