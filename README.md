# Calendar Assistant Web App

## Overview
The Calendar Assistant Web App is a web application designed to manage calendar events and provide an assistant for scheduling and communication. The system supports authenticated users to view, create, edit, and delete calendar events, as well as interact with an assistant via a chat interface.

## Features
- **Event Management**:
  - View calendar events.
  - Create new events.
  - Edit existing events.
  - Delete events.
- **Authentication**:
  - Restrict access to authenticated users.
- **Assistant Communication**:
  - Chat with an assistant for scheduling and event-related queries.

## Requirements
- Python 3.8+
- Django 4.0+
- Node.js
- Additional Python dependencies listed in `requirements.txt`.

## Installation

### Build setup
1. Clone the repository:
```bash
   git clone https://github.com/iklukowski/CalendarAssistantWebApp.git
   cd CalendarAssistantWebApp
```

2. Create a virtual environment and activate it:
```bash
    python -m venv env
    source env\\Scripts\\activate # On Windows
    source env/bin/activate # On others
```

3. Navigate to the backend directory and install dependencies:
```bash
    cd backend
    pip install -r requirements.txt
    pip install -r api/langChain/requirements.txt
```

4. Set up the database:
```bash
    python manage.py makemigrations
    python manage.py migrate
```

5. Run the development server:
```bash
    python manage.py runserver
```

6. Open a new terminal and navigate to the `frontend/` directory:
```bash
    cd ../frontend
```

7. Instal dependencies:
```bash
    npm install axios react-router-dom jwt-decode
```

8. Run the frontend development server:
```bash
    npm run dev
```

Once both development server are running, simply use the frontend interaface to use the Calendar Application in the browser.

## Testing
Ensure the terminal is place in the `backend/` folder and run:
```bash
    python manage.py test
```

## Project Structure
CalendarAssistantWebApp/
├── backend/
│   ├── api/
│   │   ├── langChain/
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── settings.py
│   └── manage.py
├── frontend/
│   ├── src/
|   |── |── components
|   |── |── |──Calendar.jsx
|   |── |── |──Form.jsx
|   |── |── |──ProtectedRoute.jsx
|   |── |── pages
|   |── |── |──Home.jsx
|   |── |── |──AssistantChat.jsx
|   |── |── |──Login.jsx
|   |── |── |──Register.jsx
|   |── |── |──NotFound.jsx
|   |── |── styles
|   |── |── |──Home.css
|   |── |── |──Form.css
|   |── |── |──Chat.css
|   |── |── App.jsx
|   |── |── api.js
│   ├── public/
│   └── package.json
└── [README.md]
