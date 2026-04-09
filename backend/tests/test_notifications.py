"""Tests for the notifications endpoints."""

from src.models.notification import Notification, NotificationType, NotificationChannel
from datetime import datetime, timezone


def _create_notification(db_session, user_id, title="Test Notification", is_read=False):
    """Helper to directly insert a notification for testing."""
    n = Notification(
        user_id=user_id,
        type=NotificationType.SYSTEM,
        title=title,
        message=f"Message for: {title}",
        is_read=is_read,
        channel=NotificationChannel.IN_APP,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(n)
    db_session.commit()
    db_session.refresh(n)
    return n


BASE = "/api/v1/notifications"


# ---------------------------------------------------------------------------
# Auth Required
# ---------------------------------------------------------------------------


def test_list_notifications_requires_auth(client):
    """GET /notifications without auth returns 401."""
    response = client.get(BASE)
    assert response.status_code == 401


def test_unread_count_requires_auth(client):
    """GET /notifications/unread-count without auth returns 401."""
    response = client.get(f"{BASE}/unread-count")
    assert response.status_code == 401


def test_preferences_requires_auth(client):
    """GET /notifications/preferences without auth returns 401."""
    response = client.get(f"{BASE}/preferences")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# List Notifications
# ---------------------------------------------------------------------------


def test_list_notifications_empty(client, test_user, auth_headers):
    """GET /notifications returns empty list initially."""
    response = client.get(BASE, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"] == []
    assert data["total"] == 0


def test_list_notifications_with_data(client, db_session, test_user, auth_headers):
    """Listing notifications returns created notifications."""
    _create_notification(db_session, test_user.id, title="First")
    _create_notification(db_session, test_user.id, title="Second")

    response = client.get(BASE, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["notifications"]) == 2


def test_list_notifications_pagination(client, db_session, test_user, auth_headers):
    """Pagination with skip and limit works."""
    for i in range(5):
        _create_notification(db_session, test_user.id, title=f"Notif {i}")

    response = client.get(f"{BASE}?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["notifications"]) == 2


# ---------------------------------------------------------------------------
# Unread Count
# ---------------------------------------------------------------------------


def test_unread_count_zero(client, test_user, auth_headers):
    """GET /notifications/unread-count returns 0 initially."""
    response = client.get(f"{BASE}/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_unread_count_reflects_unread(client, db_session, test_user, auth_headers):
    """Unread count matches number of unread notifications."""
    _create_notification(db_session, test_user.id, is_read=False)
    _create_notification(db_session, test_user.id, is_read=False)
    _create_notification(db_session, test_user.id, is_read=True)

    response = client.get(f"{BASE}/unread-count", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["count"] == 2


# ---------------------------------------------------------------------------
# Mark Read
# ---------------------------------------------------------------------------


def test_mark_notification_read(client, db_session, test_user, auth_headers):
    """PUT /notifications/{id}/read marks a single notification as read."""
    n = _create_notification(db_session, test_user.id, is_read=False)

    response = client.put(f"{BASE}/{n.id}/read", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["id"] == n.id


def test_mark_notification_read_not_found(client, test_user, auth_headers):
    """Marking a non-existent notification returns 404."""
    response = client.put(f"{BASE}/99999/read", headers=auth_headers)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Mark All Read
# ---------------------------------------------------------------------------


def test_mark_all_read(client, db_session, test_user, auth_headers):
    """PUT /notifications/read-all marks all notifications as read."""
    _create_notification(db_session, test_user.id, is_read=False)
    _create_notification(db_session, test_user.id, is_read=False)
    _create_notification(db_session, test_user.id, is_read=False)

    response = client.put(f"{BASE}/read-all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3

    # Verify unread count is now 0
    count_resp = client.get(f"{BASE}/unread-count", headers=auth_headers)
    assert count_resp.json()["count"] == 0


def test_mark_all_read_when_none_unread(client, test_user, auth_headers):
    """Mark all read with no unread notifications returns count 0."""
    response = client.put(f"{BASE}/read-all", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["count"] == 0


# ---------------------------------------------------------------------------
# Delete Notification
# ---------------------------------------------------------------------------


def test_delete_notification(client, db_session, test_user, auth_headers):
    """DELETE /notifications/{id} removes the notification."""
    n = _create_notification(db_session, test_user.id)

    response = client.delete(f"{BASE}/{n.id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it is gone
    list_resp = client.get(BASE, headers=auth_headers)
    assert list_resp.json()["total"] == 0


def test_delete_notification_not_found(client, test_user, auth_headers):
    """Deleting a non-existent notification returns 404."""
    response = client.delete(f"{BASE}/99999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_does_not_affect_others(client, db_session, test_user, auth_headers):
    """Deleting one notification does not affect other notifications."""
    n1 = _create_notification(db_session, test_user.id, title="Keep")
    n2 = _create_notification(db_session, test_user.id, title="Delete")

    client.delete(f"{BASE}/{n2.id}", headers=auth_headers)

    list_resp = client.get(BASE, headers=auth_headers)
    assert list_resp.json()["total"] == 1
    assert list_resp.json()["notifications"][0]["title"] == "Keep"


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------


def test_get_preferences_creates_defaults(client, test_user, auth_headers):
    """GET /notifications/preferences creates default preferences if none exist."""
    response = client.get(f"{BASE}/preferences", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_user.id
    # Default values
    assert data["email_enabled"] is True
    assert data["in_app_enabled"] is True
    assert data["sms_enabled"] is False
    assert data["marketing"] is False


def test_update_preferences(client, test_user, auth_headers):
    """PUT /notifications/preferences updates specific fields."""
    # Ensure defaults exist
    client.get(f"{BASE}/preferences", headers=auth_headers)

    response = client.put(
        f"{BASE}/preferences",
        json={"sms_enabled": True, "marketing": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sms_enabled"] is True
    assert data["marketing"] is True
    # Unchanged fields should remain at defaults
    assert data["email_enabled"] is True


def test_update_preferences_partial(client, test_user, auth_headers):
    """Partial update only changes specified fields."""
    # Ensure defaults exist
    client.get(f"{BASE}/preferences", headers=auth_headers)

    response = client.put(
        f"{BASE}/preferences",
        json={"compliance_reminders": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["compliance_reminders"] is False
    assert data["payment_alerts"] is True  # Unchanged
