"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from copy import deepcopy

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initial in-memory activity database
ACTIVITIES_TEMPLATE = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "waitlist": []
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "waitlist": []
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "waitlist": []
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "waitlist": []
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "waitlist": []
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "waitlist": []
    }
}

activities = deepcopy(ACTIVITIES_TEMPLATE)


def _serialize_activity(activity: dict) -> dict:
    participants = activity.get("participants", [])
    waitlist = activity.get("waitlist", [])
    return {
        "description": activity["description"],
        "schedule": activity["schedule"],
        "max_participants": activity["max_participants"],
        "participants": participants,
        "participant_count": len(participants),
        "waitlist": waitlist,
        "waitlist_count": len(waitlist)
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return {
        name: _serialize_activity(activity)
        for name, activity in activities.items()
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    participants = activity["participants"]
    waitlist = activity.setdefault("waitlist", [])

    # Validate student is not already signed up or waitlisted
    if email in participants or email in waitlist:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up or waitlisted"
        )

    if len(participants) < activity["max_participants"]:
        participants.append(email)
        return {
            "status": "enrolled",
            "message": f"Signed up {email} for {activity_name}"
        }

    waitlist.append(email)
    return {
        "status": "waitlisted",
        "position": len(waitlist),
        "message": f"{activity_name} is full. Added {email} to the waitlist"
    }


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    participants = activity["participants"]
    waitlist = activity.setdefault("waitlist", [])

    if email in participants:
        participants.remove(email)

        if waitlist:
            promoted_email = waitlist.pop(0)
            participants.append(promoted_email)
            return {
                "status": "promoted",
                "promoted_email": promoted_email,
                "message": (
                    f"Unregistered {email} from {activity_name}. "
                    f"Auto-enrolled {promoted_email} from the waitlist"
                )
            }

        return {
            "status": "unregistered",
            "message": f"Unregistered {email} from {activity_name}"
        }

    if email in waitlist:
        waitlist.remove(email)
        return {
            "status": "unregistered_waitlist",
            "message": f"Removed {email} from the waitlist for {activity_name}"
        }

    raise HTTPException(
        status_code=400,
        detail="Student is not signed up or waitlisted for this activity"
    )
