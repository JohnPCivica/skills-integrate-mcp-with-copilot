# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Enforce activity capacity limits
- Automatically place students on a waitlist when activities are full
- Auto-promote waitlisted students when a spot opens

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with participant and waitlist counts             |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Enroll in an activity or join waitlist if full                      |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from participant list or waitlist                        |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up
   - Ordered waitlist of student emails
   - Computed counts for participants and waitlist

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

## Signup and Waitlist Behavior

- If an activity has available spots, signup returns `status: "enrolled"`.
- If an activity is full, signup returns `status: "waitlisted"` and a waitlist `position`.
- If an enrolled student unregisters and the waitlist is not empty, the first waitlisted student is auto-promoted and unregister returns `status: "promoted"`.
- Duplicate entries are rejected if an email is already enrolled or already on the waitlist for the same activity.
