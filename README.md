# SPM Project

## 📋 Table of Contents
- [Frontend Setup](#frontend-setup)
- [Backend Setup](#backend-setup)
- [Microservices](#microservices)

---

## 🎨 Frontend Setup

### Prerequisites
Add `.env` file to the `frontend` folder (instructions to be provided closer to deadline)

### Installation & Running
```bash
cd frontend
npm install
npm run dev
```

**Note:** Open another terminal to run the backend microservices.

---

## 🔧 Backend Setup

### Prerequisites
Add `.env` file to the `backend` folder (instructions to be provided closer to deadline)

### General Setup Instructions for Each Microservice

We have the following microservices:
- **Comments** (backend/comments)
- **Dept** (backend/dept)
- **Notification** (backend/notification)
- **Projects** (backend/projects)
- **Report** (backend/report)
- **Tasks** (backend/tasks)
- **Team** (backend/team)
- **Users** (backend/users)

---

## 🚀 Microservices

For each microservice, follow these steps:

### 1. Navigate to the microservice folder
```bash
cd backend/[microservice-name]
```
Replace `[microservice-name]` with: `comments`, `dept`, `notification`, `projects`, `report`, `tasks`, `team`, or `users`

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
```

### 3. Activate the virtual environment

**For Mac/Linux:**
```bash
source venv/bin/activate
```

**For Windows:**
```bash
venv\Scripts\activate
```

⚠️ **IMPORTANT:** Make sure you are in the virtual environment before proceeding!

### 4. Install required libraries
```bash
pip install -r requirements.txt
```

### 5. Run the microservice
```bash
python app.py
```

---

## 📦 Additional Package Management

### To install additional libraries:
```bash
pip install [packagename]
```

### To update requirements.txt after installing new packages:
```bash
pip freeze > requirements.txt
```

---

## 🔄 Quick Start - Running All Microservices

You'll need to open separate terminal windows for each microservice you want to run:

```bash
# Terminal 1 - Comments
cd backend/comments
venv\Scripts\activate  # or source venv/bin/activate on Mac
python app.py

# Terminal 2 - Dept
cd backend/dept
venv\Scripts\activate
python app.py

# Terminal 3 - Notification
cd backend/notification
venv\Scripts\activate
python app.py

# Terminal 4 - Projects
cd backend/projects
venv\Scripts\activate
python app.py

# Terminal 5 - Report
cd backend/report
venv\Scripts\activate
python app.py

# Terminal 6 - Tasks
cd backend/tasks
venv\Scripts\activate
python app.py

# Terminal 7 - Team
cd backend/team
venv\Scripts\activate
python app.py

# Terminal 8 - Users
cd backend/users
venv\Scripts\activate
python app.py

# Terminal 9 - Frontend
cd frontend
npm run dev
```

---
