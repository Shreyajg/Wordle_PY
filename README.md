# Guess the Word

A full-stack 5-letter word guessing game built using **Python, FastAPI, MongoDB, JWT, and vanilla JavaScript**.

The application supports two roles — **Player** and **Admin** — with persistent game state, authentication, Wordle-style feedback, daily game limits, and administrative reports.

---

## Features

### Player

- User registration and login
- Username and password validation
- BCrypt password hashing
- JWT-based authentication using HttpOnly cookies
- Random selection of a 5-letter word from MongoDB
- Wordle-style feedback:
  - 🟩 **Green** — correct letter in the correct position
  - 🟨 **Orange** — correct letter in the wrong position
  - ⬜ **Grey** — letter is not present in the target word
- Maximum of **5 guesses per game**
- Maximum of **3 games per player per day**
- Guesses and game state persisted in MongoDB
- Previous guesses restored after page reload
- Validation of guesses against the stored word list
- Congratulatory message when the player wins
- "Better luck next time" message when the player loses

### Admin

- Role-based access control
- Daily report containing:
  - Number of unique users who played that day
  - Number of correct guesses
- User-specific report containing:
  - Date
  - Number of words tried
  - Number of correct guesses

---

## Tech Stack

### Backend

- Python 3.10+
- FastAPI
- Uvicorn
- PyMongo
- Pydantic
- PyJWT
- BCrypt

### Database

- MongoDB Atlas

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript

### Tools

- pip / virtualenv
- pytest
- Git / GitHub
- Postman

---

## Architecture

```text
                    ┌───────────────────────┐
                    │       Frontend        │
                    │     HTML / CSS / JS   │
                    └───────────┬───────────┘
                                │
                                │ REST API
                                ▼
                    ┌───────────────────────┐
                    │        FastAPI        │
                    │       Backend         │
                    ├───────────────────────┤
                    │ Routers / Controllers │
                    │ Services              │
                    │ Repositories          │
                    │ Models / Schemas      │
                    │ Authentication        │
                    │ Authorization         │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     MongoDB Atlas     │
                    ├───────────────────────┤
                    │ Users                 │
                    │ Words                 │
                    │ Games                 │
                    └───────────────────────┘
```

---

## Project Structure

```text
guess-game/
│
├── Backend/
│   ├── app/
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── cors.py
│   │   │   └── seeder.py
│   │   │
│   │   ├── controller/
│   │   │   ├── auth.py
│   │   │   ├── game.py
│   │   │   └── admin.py
│   │   │
│   │   ├── exception/
│   │   │   ├── exceptions.py
│   │   │   └── handlers.py
│   │   │
│   │   ├── model/
│   │   │   ├── user.py
│   │   │   ├── word.py
│   │   │   ├── game.py
│   │   │   └── enums.py
│   │   │
│   │   ├── repository/
│   │   │   ├── user_repository.py
│   │   │   ├── word_repository.py
│   │   │   └── game_repository.py
│   │   │
│   │   ├── service/
│   │   │   ├── auth_service.py
│   │   │   ├── game_service.py
│   │   │   ├── admin_service.py
│   │   │   └── jwt_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
│
├── Frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

## Game Flow

```text
Login / Register
       │
       ▼
   Start Game
       │
       ▼
Random 5-letter word
       │
       ▼
  Submit Guess
       │
       ├────────────── Correct ──────────────► WON
       │                                        │
       │                                        ▼
       │                               Congratulations
       │                                        │
       │                                        ▼
       │                                      [ OK ]
       │                                        │
       │                                        ▼
       │                                   Game stops
       │
       └────────────── Incorrect
                              │
                              ▼
                       Guesses remaining?
                         │           │
                        YES          NO
                         │           │
                         ▼           ▼
                      Continue      LOST
                                     │
                                     ▼
                           Better luck next time
                                     │
                                     ▼
                                   [ OK ]
                                     │
                                     ▼
                                Game stops
```

---

## Authentication

```text
Login
  │
  ▼
Validate credentials
  │
  ▼
Generate JWT
  │
  ▼
Store JWT in HttpOnly cookie
  │
  ▼
Authenticated requests
```

JWT authentication is handled using an **HttpOnly cookie**.

---

## Role-Based Authorization

The application supports two roles:

- `PLAYER`
- `ADMIN`

Player endpoints require authentication.

Admin endpoints additionally require the `ADMIN` role.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new player |
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout |
| GET | `/auth/me` | Get the authenticated user |

### Player / Game

| Method | Endpoint | Description |
|---|---|---|
| POST | `/games/start` | Start or resume a game |
| POST | `/games/guess` | Submit a guess |
| GET | `/games/current` | Retrieve the current game |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/daily-report` | Get daily statistics |
| GET | `/admin/user-report/{playerId}` | Get statistics for a specific player |

### API Documentation

FastAPI provides interactive API documentation at:

`http://localhost:8080/docs`

while the backend is running.

---

## Database

### User

```text
id
username
passwordHash
role
```

### Word

```text
id
word
```

### Game

```text
id
playerId
targetWord
guesses
status
createdAt
```

Game status can be:

```text
IN_PROGRESS
WON
LOST
```

The word list is seeded with **20 words** when the `words` collection is empty.

---

## Daily Game Limit

Each player can start a maximum of **3 games per day**.

When starting a game, the backend checks the number of games created by the player during the current day.

If an `IN_PROGRESS` game already exists, it is resumed instead of creating another game.

---

## Game Persistence

Game state is persisted in MongoDB.

When a player submits a guess:

```text
Guess
  │
  ▼
Validate guess
  │
  ▼
Calculate feedback
  │
  ▼
Update game
  │
  ▼
Save game to MongoDB
```

If the page is refreshed while a game is still in progress:

```text
Page Reload
    │
    ▼
GET /games/current
    │
    ▼
Retrieve IN_PROGRESS game
    │
    ▼
Return previous guesses + results
    │
    ▼
Restore guesses in frontend
```

The target word is not exposed while the game is in progress.

---

## Admin Reports

### Daily Report

The daily report provides:

- Number of unique users who played on the selected date
- Number of correct guesses

Example:

```json
{
    "noOfUsers": 10,
    "noOfCorrectGuesses": 6
}
```

### User Report

The user report provides statistics for a specific player on a selected date.

Example:

```json
{
    "date": "2026-09-23",
    "noOfWordsTried": 1,
    "noOfCorrectGuesses": 0
}
```

---

## Making an Admin

There is no admin sign-up.

Register a normal user first, then change the user's role directly in MongoDB:

```javascript
db.users.updateOne(
    { username: "YourName" },
    { $set: { role: "ADMIN" } }
)
```

---

# Running Locally

## Prerequisites

- Python 3.10 or later
- MongoDB Atlas account
- Git

## 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd guess-game
```

## 2. Create a Virtual Environment

Navigate to the `Backend` directory.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```text
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_secret_key
```

Keep `.env` out of version control.

## 5. Start the Backend

From the `Backend` directory:

```bash
python -m app.main
```

The backend runs at:

```text
http://localhost:8080
```

FastAPI documentation:

```text
http://localhost:8080/docs
```

## 6. Start the Frontend

From the `Frontend` directory:

```bash
python -m http.server 5500
```

Open:

```text
http://localhost:5500
```

---

# Testing

The application was tested for:

- User registration
- Username and password validation
- Login and logout
- JWT authentication
- Role-based authorization
- Game creation
- Random word selection
- Word validation
- GREEN / ORANGE / GREY feedback
- Correct guesses
- Congratulatory message
- Failed games
- Better luck next time message
- Five-guess limit
- Three-games-per-day limit
- Persistence of guesses
- Game restoration after page reload
- MongoDB persistence
- Daily admin reports
- User-specific admin reports
- CORS configuration
- REST API testing using Postman

Run automated tests with:

```bash
pip install -r requirements-dev.txt
pytest
```

---

# Security

The application uses:

- BCrypt password hashing
- JWT authentication
- HttpOnly authentication cookies
- Role-based authorization
- Protected admin endpoints
- CORS configuration
- Environment variables for secrets

---

# Screenshots

## Admin Login

![Admin Login](https://github.com/user-attachments/assets/81a3c224-3ff4-43f9-a322-4227d24a6879)

## Admin Dashboard

![Admin Dashboard](https://github.com/user-attachments/assets/a702e853-0415-42d6-8c0b-4be41e86fffd)

## Player Login

![Player Login](https://github.com/user-attachments/assets/de2553d8-b5b9-4ed3-9541-d737750eb2bc)

## Game Won

![Game Won](https://github.com/user-attachments/assets/8ead572f-0be0-458c-ba39-1a05b9df2362)

## Game Lost

![Game Lost](https://github.com/user-attachments/assets/e53a3845-b1e6-41dd-be0a-470bd5d13024)

## Three Games Per Day Limit

![Three Games Per Day Limit](https://github.com/user-attachments/assets/b978e1b8-84bc-40ab-8a15-995e500ffe43)

---

# Author

**Shreya Jaganatha Gowda**
