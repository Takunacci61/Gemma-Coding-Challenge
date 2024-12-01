# Gemma-Coding-Challenge-
This project was developed as a solution for the Gemma Coding Challenge

# 📘 Noma's Planner

**Planner App**  
A comprehensive 30-day planner application with a **Django backend** and a **Flutter frontend**, designed to help users manage their goals, daily routines, and activities seamlessly.

---

## 🚀 Features

### Backend (Django)
- User authentication (JWT-based).
- Goal management:
  - Create, view, and update goals.
- Routine management:
  - Create, view, and update daily routines.
- Activity management:
  - Plan daily activities and mark them as completed.
- Calendar integration for goal timelines.
- API endpoints secured with authentication.

### Frontend (Flutter)
- **User Interface**:
  - Intuitive and modern design with smooth animations.
- **Dashboard**:
  - Displays user goals, routines, and daily plans in an interactive format.
- **Goal Management**:
  - Add, edit, and view goals with start and end dates.
- **Routine Management**:
  - Schedule daily routines with start and end times.
- **Activity Tracking**:
  - Manage daily activities with status tracking.
- Calendar view for goals and routines.

---

## 🛠️ Tech Stack

- **Backend**: Django, Django Rest Framework
  - Database: PostgreSQL
  - Authentication: JWT
- **Frontend**: Flutter
  - UI Library: Material Design
- **Other Tools**:
  - Shared Preferences for local storage (Flutter).
  - Table Calendar for Flutter.
  - Docker (optional for deployment).

---

## 🗂️ Project Structure

### Backend (Django)

The folder structure for the backend is as follows (referenced from the shared image):

```
planner-backend/
├── planner_backend/        # Django project root
│   ├── settings.py         # Project settings
│   ├── urls.py             # URL configurations
│   ├── wsgi.py             # WSGI entry point for the app
│   └── asgi.py             # ASGI entry point for asynchronous support
├── accounts/               # Handles user authentication and profiles
│   ├── migrations/         # Database migrations for accounts
│   ├── admin.py            # Django admin configurations for accounts
│   ├── apps.py             # App configuration
│   ├── models.py           # Models for user accounts
│   ├── serializers.py      # Serializers for accounts API
│   ├── urls.py             # URL patterns for accounts
│   └── views.py            # Logic for accounts (e.g., login, profile)
├── planner_app/            # Handles goals, routines, and activities
│   ├── migrations/         # Database migrations for planner_app
│   ├── admin.py            # Django admin configurations for planner data
│   ├── apps.py             # App configuration
│   ├── models.py           # Models for goals, routines, and activities
│   ├── serializers.py      # Serializers for planner_app API
│   ├── urls.py             # URL patterns for planner_app
│   ├── utils.py            # Utility functions for planner_app
│   └── views.py            # Logic for goals, routines, and activities
├── media/                  # Media storage (e.g., uploads)
└── manage.py               # Django's CLI tool
```

### Frontend (Flutter)

The folder structure for the Flutter frontend is as follows (referenced from the shared image):

```
planner-frontend/
├── lib/
│   ├── screens/            # Flutter screens (Dashboard, Goals, Routines, Profile)
│   │   ├── dashboard_page.dart
│   │   ├── goals_page.dart
│   │   ├── routine_page.dart
│   │   ├── profile_page.dart
│   │   └── login_page.dart
│   ├── widgets/            # Reusable UI components (e.g., buttons, cards, modals)
│   │   ├── bottom_menu.dart
│   │   └── custom_appbar.dart
│   ├── services/           # API services for network requests
│   │   ├── api_service.dart
│   │   └── auth_service.dart
│   ├── models/             # Data models for API responses
│   │   ├── user_model.dart
│   │   └── goal_model.dart
│   ├── utils/              # Utility functions (e.g., formatters, constants)
│   │   └── date_utils.dart
│   └── main.dart           # Application entry point
├── assets/                 # Static assets like images and fonts
│   ├── images/             # App images
│   └── fonts/              # Custom fonts
├── pubspec.yaml            # Flutter dependencies
└── README.md               # Frontend-specific instructions
```

---

## 🔧 Setup Instructions

### Backend
1. Clone the repository:
   ```bash
   git clone https://github.com/username/planner-app.git
   cd planner-backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

5. (Optional) Run the backend in Docker:
   ```bash
   docker-compose up --build
   ```

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd planner-frontend
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Run the app:
   ```bash
   flutter run
   ```

4. Configure the backend API URL in `lib/services/api_service.dart`:
   ```dart
   const String BASE_URL = "http://127.0.0.1:8000/api";
   ```

---

## 🔑 API Endpoints

### Authentication
- `POST /api/token/`: Obtain JWT tokens.
- `POST /api/token/refresh/`: Refresh JWT token.

### Goals
- `GET /api/goals/`: Fetch all goals.
- `POST /api/goals/`: Create a goal.
- `GET /api/goals/<id>/`: Fetch details of a specific goal.

### Routines
- `GET /api/routines/`: Fetch all routines.
- `POST /api/routines/`: Create a routine.

### Activities
- `GET /api/activities/`: Fetch all activities.
- `PATCH /api/activities/<id>/`: Update activity status.

---

## 🌐 Deployment

### Backend
- Use Gunicorn for production.
- Deploy to a cloud provider like AWS, DigitalOcean, or Heroku.

### Frontend
- Compile the Flutter app for release:
  ```bash
  flutter build apk --release
  ```
- Distribute the APK via Google Play Store or other platforms.

---

## 🧪 Testing

### Backend
Run tests with Django's test suite:
```bash
python manage.py test
```

### Frontend
Run Flutter tests:
```bash
flutter test
```
![Screenshot 2024-12-01 at 12 41 25](https://github.com/user-attachments/assets/8334890b-b1d3-4b8f-adba-f6f305b12aae)

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing
1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push to the branch:
   ```bash
   git push origin feature-name
   ```
4. Create a pull request on GitHub.

---

## 👥 Authors

- **Takunacci** - Backend Developer
- **Takunacci** - Frontend Developer

For questions or collaboration, contact us at [simbanyagweta@gmail.com].

