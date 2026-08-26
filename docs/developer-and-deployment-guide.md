# RaktDaan Developer, Deployment & DevOps Guide v2.0

## Table of Contents
1. [Developer Onboarding & Environment Setup](#1-developer-onboarding--environment-setup)
2. [Docker Containerization](#2-docker-containerization)
3. [Kubernetes Deployment Manifests](#3-kubernetes-deployment-manifests)
4. [Continuous Integration (CI/CD) Workflow](#4-continuous-integration-cicd-workflow)
5. [Database Migration Strategy (Alembic)](#5-database-migration-strategy-alembic)
6. [Team Integration Matrix](#6-team-integration-matrix)

---

## 1. Developer Onboarding & Environment Setup

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git 2.30+
- Virtualenv package

### Step-by-Step Local Environment Setup
```bash
# 1. Clone the repository and navigate into project directory
git clone https://github.com/RaktDaan/RaktDaan1.git
cd RaktDaan1

# 2. Checkout feature branch
git checkout feature/auth-database

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Copy environment configuration
cp .env.example .env

# 7. Run database seed & verify CLI
python -m scripts.cli status

# 8. Run unit test suite
python -m pytest -v

# 9. Start development server
python -m app.main
```

---

## 2. Docker Containerization

### `Dockerfile` Configuration
```dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.main:app"]
```

---

## 3. Kubernetes Deployment Manifests

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: raktdaan-backend
  labels:
    app: raktdaan-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: raktdaan-backend
  template:
    metadata:
      labels:
        app: raktdaan-backend
    spec:
      containers:
      - name: backend
        image: raktdaan/backend:2.0.0
        ports:
        - containerPort: 5000
        envFrom:
        - secretRef:
            name: raktdaan-secrets
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 15
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: raktdaan-backend-service
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 5000
  selector:
    app: raktdaan-backend
```

---

## 4. Continuous Integration (CI/CD) Workflow

### GitHub Actions Pipeline (`.github/workflows/ci.yml`)
```yaml
name: RaktDaan CI/CD Pipeline

on:
  push:
    branches: [ main, feature/auth-database ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run Pytest Test Suite
      run: |
        python -m pytest -v
        
    - name: Verify CLI Status
      run: |
        python -m scripts.cli status
```

---

## 5. Team Integration Matrix

| Member | Feature Responsibility | Integration Mechanism | Key Models / APIs |
| :--- | :--- | :--- | :--- |
| **Member 1 (Done)** | Auth & DB Foundation | Exposes `db`, `BaseModelMixin`, `@require_donor`, `@require_admin` | `User`, `DonorProfile`, `UserSession`, `SecurityAuditLog` |
| **Member 2** | Home & Frontend UI | Consumes Auth REST API (`/register`, `/donor/login`, `/admin/login`) | `TokenResponse`, `UserResponse`, `ErrorResponse` |
| **Member 3** | Donor Module | Imports `db`, `DonorProfile` for appointments & donations | `DonorProfile`, `BloodBag`, `DonorMedicalHistory` |
| **Member 4** | Blood Inventory | Imports `db`, `BloodInventory` for bag tracking & stock | `BloodInventory`, `BloodBag`, `BloodCompatibilityMatrix` |
| **Member 5** | Blood Request & Admin | Imports `db`, `@require_admin` for approval workflows | `BloodRequest`, `RequestFulfillment`, `SecurityAuditLog` |
