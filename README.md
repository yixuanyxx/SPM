# SPM
## FRONTEND
### Add .env file to frontend folder
- figure out instructions closer to deadline
### Install necessary packages
```cd frontend```
```npm install```
### Start the app in browser
```npm run dev```


NOTE: open another terminal to run backend
## BACKEND SET UP FIRST TIME (for us)
### Add .env file to backend folder
- figure out instructions closer to deadline

============================================================
### Create a virtual environment inside task microservice
```cd backend/tasks```
```python -m venv venv```

### Activate virtual environment
For mac:
```source venv/bin/activate```
For windows:
```venv\Scripts\activate```
!!! IMPORTANT: MAKE SURE U ARE IN THE VENV

### Install python libraries
```pip install -r requirements.txt```

### Install any additional libraries
```pip install [packagename]```

### ADD THE LIBRARIES TO requirements.txt
```pip freeze > requirements.txt```

### To run the task microservice:
```python app.py```
(task microservice runs on port 5002)

===================================================

### Create a virtual environment inside projects microservice
```cd backend/projects```
```python -m venv venv```

### Activate virtual environment
For mac:
```source venv/bin/activate```
For windows:
```venv\Scripts\activate```
!!! IMPORTANT: MAKE SURE U ARE IN THE VENV

### Install python libraries
```pip install -r requirements.txt```

### Install any additional libraries
```pip install [packagename]```

### ADD THE LIBRARIES TO requirements.txt
```pip freeze > requirements.txt```

### To run the project microservice:
```python app.py```
(task microservice runs on port 5001)

===================================================

## BACKEND SET UP FIRST TIME (for instructor)
### Add .env file to backend folder
- figure out instructions closer to deadline
### Create a virtual environment (optional)
```cd backend```
```python -m venv venv```
For mac:
```source venv/bin/activate```
For windows:
```venv\Scripts\activate```
### Install python libraries
```pip install -r requirements.txt```
====================================================


