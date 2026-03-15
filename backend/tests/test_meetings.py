"""Tests for the meetings management endpoints."""

from datetime import datetime, timedelta
from unittest.mock import patch


# Use naive datetimes to avoid SQLite timezone mismatch (SQLite does not store
# timezone info, so datetime comparisons in the app code would fail with
# "can't subtract offset-naive and offset-aware datetimes" if we passed TZ-aware dates).
FUTURE_DATE = (datetime.utcnow() + timedelta(days=30)).isoformat()
PAST_DATE = (datetime.utcnow() - timedelta(days=5)).isoformat()


# ---------------------------------------------------------------------------
# Create Meeting
# ---------------------------------------------------------------------------


def test_create_meeting(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/meetings creates a scheduled meeting."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "First Board Meeting",
            "meeting_date": FUTURE_DATE,
            "venue": "Registered Office, Bangalore",
            "attendees": [
                {"name": "Director A", "din": "12345678", "designation": "Director"},
                {"name": "Director B", "din": "87654321", "designation": "Director"},
            ],
            "agenda_items": [
                {"item_number": 1, "title": "Approval of accounts"},
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["meeting_type"] == "BOARD_MEETING"
    assert data["title"] == "First Board Meeting"
    assert data["status"] == "scheduled"
    assert data["meeting_number"] == 1


def test_create_meeting_requires_auth(client, test_company):
    """POST /api/v1/companies/{id}/meetings without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Unauthorized Meeting",
            "meeting_date": FUTURE_DATE,
        },
    )
    assert response.status_code == 401


def test_create_meeting_invalid_type_returns_400(
    client, test_user, auth_headers, test_company
):
    """Creating a meeting with an invalid type returns 400."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "INVALID_TYPE",
            "title": "Bad Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_create_meeting_sequential_numbering(
    client, test_user, auth_headers, test_company
):
    """Multiple meetings of the same type get sequential meeting numbers."""
    for i in range(3):
        resp = client.post(
            f"/api/v1/companies/{test_company.id}/meetings/",
            json={
                "meeting_type": "BOARD_MEETING",
                "title": f"Board Meeting {i + 1}",
                "meeting_date": FUTURE_DATE,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["meeting_number"] == i + 1


# ---------------------------------------------------------------------------
# List Meetings
# ---------------------------------------------------------------------------


def test_list_meetings(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/meetings returns all meetings."""
    # Create a meeting first
    client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Board Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/meetings/",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_meetings_filter_by_type(
    client, test_user, auth_headers, test_company
):
    """List meetings can filter by meeting_type."""
    # Create meetings of different types
    client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Board Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "AGM",
            "title": "Annual General Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/meetings/?meeting_type=AGM",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(m["meeting_type"] == "AGM" for m in data)


# ---------------------------------------------------------------------------
# Get Meeting
# ---------------------------------------------------------------------------


def test_get_meeting(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/meetings/{id} returns meeting details."""
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Get Test Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )
    meeting_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/companies/{test_company.id}/meetings/{meeting_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == meeting_id
    assert data["title"] == "Get Test Meeting"


def test_get_nonexistent_meeting_returns_404(
    client, test_user, auth_headers, test_company
):
    """Getting a non-existent meeting returns 404."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/meetings/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Generate Notice
# ---------------------------------------------------------------------------


def test_generate_notice(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/meetings/{id}/notice generates notice HTML."""
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Notice Test Meeting",
            "meeting_date": FUTURE_DATE,
            "venue": "Test Venue",
        },
        headers=auth_headers,
    )
    meeting_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/{meeting_id}/notice",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["notice_html"] is not None
    assert "NOTICE" in data["notice_html"]
    assert data["status"] == "notice_sent"


# ---------------------------------------------------------------------------
# Generate Minutes
# ---------------------------------------------------------------------------


def test_generate_minutes(client, test_user, auth_headers, test_company):
    """POST /api/v1/companies/{id}/meetings/{id}/minutes generates minutes HTML."""
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Minutes Test Meeting",
            "meeting_date": FUTURE_DATE,
            "attendees": [
                {"name": "Director A", "din": "12345678", "present": True},
            ],
        },
        headers=auth_headers,
    )
    meeting_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/{meeting_id}/minutes",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["minutes_html"] is not None
    assert "MINUTES" in data["minutes_html"]
    assert data["status"] == "minutes_draft"


# ---------------------------------------------------------------------------
# Sign Minutes
# ---------------------------------------------------------------------------


def test_sign_minutes(client, test_user, auth_headers, test_company):
    """PUT /api/v1/companies/{id}/meetings/{id}/minutes/sign marks minutes as signed."""
    # Create meeting and generate minutes
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Sign Test Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )
    meeting_id = create_resp.json()["id"]

    client.post(
        f"/api/v1/companies/{test_company.id}/meetings/{meeting_id}/minutes",
        headers=auth_headers,
    )

    # Patch datetime.now in the meetings router to return a naive datetime,
    # because SQLite strips timezone info from stored datetimes. The router
    # computes (now - meeting.meeting_date).days which fails when one is
    # tz-aware and the other is naive.
    naive_now = datetime.utcnow()
    with patch("src.routers.meetings.datetime") as mock_dt:
        mock_dt.now.return_value = naive_now
        mock_dt.fromisoformat = datetime.fromisoformat
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        response = client.put(
            f"/api/v1/companies/{test_company.id}/meetings/{meeting_id}/minutes/sign",
            json={"signed_by": "Director A"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert data["minutes_signed"] is True
    assert data["minutes_signed_by"] == "Director A"
    assert data["status"] == "minutes_signed"


def test_sign_minutes_without_generating_returns_400(
    client, test_user, auth_headers, test_company
):
    """Signing minutes without generating them first returns 400."""
    create_resp = client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "No Minutes Meeting",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )
    meeting_id = create_resp.json()["id"]

    response = client.put(
        f"/api/v1/companies/{test_company.id}/meetings/{meeting_id}/minutes/sign",
        json={"signed_by": "Director A"},
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Upcoming Meetings
# ---------------------------------------------------------------------------


def test_list_upcoming_meetings(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/meetings/upcoming returns future meetings."""
    # Create a future meeting
    client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "AGM",
            "title": "Future AGM",
            "meeting_date": FUTURE_DATE,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/meetings/upcoming",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# ---------------------------------------------------------------------------
# Minutes Pending
# ---------------------------------------------------------------------------


def test_list_minutes_pending(client, test_user, auth_headers, test_company):
    """GET /api/v1/companies/{id}/meetings/minutes-pending returns past meetings without signed minutes."""
    # Create a past meeting (minutes not signed)
    client.post(
        f"/api/v1/companies/{test_company.id}/meetings/",
        json={
            "meeting_type": "BOARD_MEETING",
            "title": "Past Meeting",
            "meeting_date": PAST_DATE,
        },
        headers=auth_headers,
    )

    # Patch datetime.now in the meetings router to return a naive datetime,
    # because SQLite strips timezone info from stored datetimes.
    naive_now = datetime.utcnow()
    with patch("src.routers.meetings.datetime") as mock_dt:
        mock_dt.now.return_value = naive_now
        mock_dt.fromisoformat = datetime.fromisoformat
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        response = client.get(
            f"/api/v1/companies/{test_company.id}/meetings/minutes-pending",
            headers=auth_headers,
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Each pending item should have days_since_meeting
    for item in data:
        assert "days_since_meeting" in item
