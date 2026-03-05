import unittest
from copy import deepcopy

from fastapi import HTTPException

from src import app


class WaitlistBehaviorTests(unittest.TestCase):
    def setUp(self):
        app.activities = deepcopy(app.ACTIVITIES_TEMPLATE)

    def test_full_activity_signup_gets_waitlisted(self):
        activity_name = "Chess Club"
        activity = app.activities[activity_name]
        activity["max_participants"] = len(activity["participants"])

        result = app.signup_for_activity(activity_name, "newstudent@mergington.edu")

        self.assertEqual(result["status"], "waitlisted")
        self.assertEqual(result["position"], 1)
        self.assertIn("newstudent@mergington.edu", activity["waitlist"])

    def test_waitlist_auto_promotion_is_fifo(self):
        activity_name = "Chess Club"
        activity = app.activities[activity_name]
        activity["max_participants"] = len(activity["participants"])

        app.signup_for_activity(activity_name, "first@mergington.edu")
        app.signup_for_activity(activity_name, "second@mergington.edu")

        removed = activity["participants"][0]
        result = app.unregister_from_activity(activity_name, removed)

        self.assertEqual(result["status"], "promoted")
        self.assertEqual(result["promoted_email"], "first@mergington.edu")
        self.assertIn("first@mergington.edu", activity["participants"])
        self.assertEqual(activity["waitlist"], ["second@mergington.edu"])

    def test_duplicate_signup_rejected_for_participant_or_waitlist(self):
        activity_name = "Chess Club"
        activity = app.activities[activity_name]
        enrolled_email = activity["participants"][0]

        with self.assertRaises(HTTPException) as enrolled_error:
            app.signup_for_activity(activity_name, enrolled_email)
        self.assertEqual(enrolled_error.exception.status_code, 400)

        activity["max_participants"] = len(activity["participants"])
        app.signup_for_activity(activity_name, "queued@mergington.edu")

        with self.assertRaises(HTTPException) as queued_error:
            app.signup_for_activity(activity_name, "queued@mergington.edu")
        self.assertEqual(queued_error.exception.status_code, 400)

    def test_activities_payload_contains_counts(self):
        data = app.get_activities()

        chess = data["Chess Club"]
        self.assertIn("participant_count", chess)
        self.assertIn("waitlist_count", chess)
        self.assertEqual(chess["participant_count"], len(chess["participants"]))
        self.assertEqual(chess["waitlist_count"], len(chess["waitlist"]))


if __name__ == "__main__":
    unittest.main()
