# 🌿 AGROS

**Next-Generation Cardamom Estate Management System**

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

---

## 📖 Overview

**AGROS** is a comprehensive, enterprise-grade web application designed specifically for the management of cardamom estates. Built on the robust Django framework, AGROS digitizes and streamlines every aspect of plantation operations—from labor attendance and task assignments to harvest tracking and dynamic payroll calculations.

Whether you're an Estate Manager tracking daily yields or an Administrator overseeing global payroll across multiple plantations, AGROS provides a centralized, secure, and intuitive command center.

## ✨ Key Features

### 👥 Role-Based Access Control
- **Administrator**: Global overview, verification queues, access logs, and complete financial visibility.
- **Estate Manager**: Estate-specific activity logging, task assignments, and labor roster management.
- **Worker**: Personalized dashboard showing recent task assignments, attendance history, and status updates.

### 🚜 Operations Management
- **Estates & Plots**: Organize and track data across multiple estates and individual plots.
- **Activities & Tasks**: Assign specific tasks (e.g., Weed Clearing, Pruning, Fertilizing) to workers and track completion.
- **Harvest Production**: Log daily yields and monitor output across all plots.

### 💰 Labor & Payroll System
- **Attendance Tracking**: Bulk-mark daily attendance for the entire workforce.
- **Dynamic Payroll**: Automatic calculation of earnings based on actual attendance days and a configurable Base Wage.
- **Payment Records**: Record payouts and maintain an accurate, real-time "Balance Due" for every worker.

### 📊 Reporting & Analytics
- **Dynamic Dashboards**: Real-time statistics, pending approvals, and system activity pulse.
- **Data Export**: Instantly generate and download comprehensive CSV and PDF reports for offline analysis.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MySQL Server

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/codespace-design/agros.git
   cd agros
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**
   - Create a MySQL database named `agros`.
   - Ensure the credentials in `agros/settings.py` match your local setup.

5. **Apply Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Seed Professional Data (Optional but Recommended)**
   Populate the database with 5 years of realistic historical data (Estates, Users, Tasks, and Payroll).
   ```bash
   python seed_professional_data.py
   ```
   *Default Accounts Created:*
   - Admin: `admin` / `adminpassword`
   - Manager: `manager` / `managerpassword`
   - Worker: e.g., `ravi_kumar` / `workerpassword`

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000/` in your browser.

---

## 🛠️ Tech Stack
- **Backend**: Django, Python
- **Database**: MySQL
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, FontAwesome
- **Reporting**: ReportLab (PDF), Python CSV module
