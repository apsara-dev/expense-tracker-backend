# FinTrack Project Documentation & Master Interview Kit

Welcome to the comprehensive documentation suite for **FinTrack - Full-Stack Wealth & Expense Management Platform**.

This folder contains all the technical study material, architecture diagrams, sequence flows, database ERDs, API contracts, future roadmaps, and interview questions prepared specifically for technical viva, project presentations, and job interviews.

---

## Complete Documentation Index

### 👑 [04. COMPLETE MASTER STUDY & ARCHITECTURE GUIDE (04_COMPLETE_MASTER_STUDY_GUIDE.md)](./04_COMPLETE_MASTER_STUDY_GUIDE.md) ⭐ *(Recommended First Read)*
* **Executive Summary & Platform Blueprint**
* **Complete Features Directory** (Authentication, Budgeting, Charts, Reports, Backups)
* **High-Level System Architecture Diagram** (Mermaid)
* **Detailed Sequence Flow Diagrams:**
  1. Two-Factor Authentication (2FA) OTP Lifecycle & Email Dispatch
  2. Transaction Creation & Reactive Chart Calculations
  3. Atomic Backup Restoration & Rollback Mechanics
* **Database Entity Relationship Diagram (ERD)** with Full Schema Specifications
* **Complete REST API Contract & Endpoint Reference Table**
* **Frontend & Backend Deep-Dive Technical Implementation**
* **DevOps, CI/CD Webhook & Cloud Deployment Flow**
* **Future Enterprise Roadmap & Scalability Plans** (PostgreSQL, Bank APIs, AI Forecasting)

---

### 📄 [01. Project Summary & Architecture (01_PROJECT_SUMMARY.md)](./01_PROJECT_SUMMARY.md)
* High-Level Project Pitch & Executive Summary
* Problem Statement vs. Proposed Solution
* Complete Technology Stack & Tools Breakdown (React 19, Vite, Chart.js, Django, DRF, SQLite, SimpleJWT, SMTP)
* System Architecture & Flow Diagrams

### 📚 [02. Technical Study Notes & Architecture Guide (02_STUDY_NOTES.md)](./02_STUDY_NOTES.md)
* Frontend Architecture: Component hierarchy, React 19 Hooks (`useMemo`, `useState`, `useEffect`), Axios request interceptors, SPA routing (`vercel.json`).
* Backend Architecture: Django REST Framework, ModelSerializers, Generics, Dual-Slash URL routing.
* Database Design: Table schemas (`Transaction`, `LoginOTP`, `PasswordResetOTP`).
* Security & Authentication: 2FA OTP protocol, 10-minute TTL, Replay attack prevention, PBKDF2 password hashing.
* Email & SMTP Engine: Google App Password setup, Gmail port 587 TLS, Responsive HTML email templates.

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
