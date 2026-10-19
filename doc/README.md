# FinTrack Project Documentation & Interview Preparation Kit

Welcome to the comprehensive documentation suite for **FinTrack - Full-Stack Wealth & Expense Management Platform**.

This folder contains all the technical study material, architecture diagrams, feature breakdowns, and interview questions and answers prepared specifically for technical viva, project presentations, and job interviews.

---

## Documentation Index

### 📄 [01. Project Summary & Architecture (01_PROJECT_SUMMARY.md)](./01_PROJECT_SUMMARY.md)
* **High-Level Project Pitch & Executive Summary**
* **Problem Statement vs. Proposed Solution**
* **Detailed Core Features Table** (2FA, Budgets, Analytics, Reports, Backup/Restore)
* **Complete Technology Stack & Tools Breakdown** (React 19, Vite, Chart.js, Django, DRF, SQLite, SimpleJWT, SMTP)
* **System Architecture Diagram** (Client <-> API <-> Backend <-> Database)
* **End-to-End User Journey Sequence Diagram**

### 📚 [02. Technical Study Notes & Architecture Guide (02_STUDY_NOTES.md)](./02_STUDY_NOTES.md)
* **Frontend Architecture:** Component hierarchy, React 19 Hooks (`useMemo`, `useState`, `useEffect`), Axios request interceptors, SPA routing (`vercel.json`).
* **Backend Architecture:** Django REST Framework, ModelSerializers, Generics, Dual-Slash URL routing.
* **Database Design:** Entity Relationship Diagram (ERD), Table schemas (`Transaction`, `LoginOTP`, `PasswordResetOTP`).
* **Security & Authentication:** 2FA OTP protocol, 10-minute TTL, Replay attack prevention, PBKDF2 password hashing.
* **Email & SMTP Engine:** Google App Password setup, Gmail port 587 TLS, Responsive HTML email templates.
* **DevOps & Cloud:** PythonAnywhere WSGI worker reload, CI/CD GitHub Webhook integration.

### 🎯 [03. Technical Interview Questions & Answers (03_INTERVIEW_QUESTIONS_AND_ANSWERS.md)](./03_INTERVIEW_QUESTIONS_AND_ANSWERS.md)
* **Section 1:** "Tell me about your project" (The 60-second high-impact pitch)
* **Section 2:** React & Frontend Concepts (React 19, Vite vs CRA, SPA routing, Chart.js)
* **Section 3:** Django & REST APIs (DRF, Serializers, Permissions, CORS)
* **Section 4:** Authentication & Security (2FA OTP, SimpleJWT, Access vs Refresh tokens)
* **Section 5:** Email & Google SMTP (App passwords, HTML vs plain text)
* **Section 6:** Real-World Challenges & Debugging (Django Trailing Slash 500 bug, SMTP BadCredentials, Vercel 404 rewrite)
* **Section 7:** Database & Performance (ACID atomic transactions, SQLite vs PostgreSQL scaling)
* **Section 8:** Rapid-Fire Technical Cheat Sheet

---

## Quick Reference Links
* **Live Hosted Backend:** [https://apsarar.pythonanywhere.com/api/](https://apsarar.pythonanywhere.com/api/)
* **Frontend Local Server:** [http://localhost:5173/](http://localhost:5173/)
* **Backend Repository:** [apsara-dev/expense-tracker-backend](https://github.com/apsara-dev/expense-tracker-backend)
* **Frontend Repository:** [apsara-dev/expense-tracker-frontend](https://github.com/apsara-dev/expense-tracker-frontend)
