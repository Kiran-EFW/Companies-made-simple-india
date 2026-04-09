"""Tests for chatbot and copilot endpoints."""

import pytest


# ---------------------------------------------------------------------------
# Chatbot — POST /chatbot/message
# ---------------------------------------------------------------------------


def test_chatbot_message_no_auth(client):
    """POST /chatbot/message works without auth (uses get_optional_user)."""
    response = client.post(
        "/api/v1/chatbot/message",
        json={"message": "What is GST?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_chatbot_message_with_auth(client, test_user, auth_headers):
    """POST /chatbot/message with auth also succeeds."""
    response = client.post(
        "/api/v1/chatbot/message",
        json={"message": "What is GST?"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data


def test_chatbot_message_with_company_context(
    client, test_user, auth_headers, test_company
):
    """POST /chatbot/message with company_id adds company context."""
    response = client.post(
        "/api/v1/chatbot/message",
        json={
            "message": "What should I do next?",
            "company_id": test_company.id,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_chatbot_message_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """POST /chatbot/message with non-owned company_id returns 404."""
    response = client.post(
        "/api/v1/chatbot/message",
        json={
            "message": "Hello",
            "company_id": 99999,
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Chatbot — GET /chatbot/suggested-questions
# ---------------------------------------------------------------------------


def test_chatbot_suggested_questions(client, test_user, auth_headers):
    """GET /chatbot/suggested-questions returns a list of questions."""
    response = client.get(
        "/api/v1/chatbot/suggested-questions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) > 0


def test_chatbot_suggested_questions_with_company(
    client, test_user, auth_headers, test_company
):
    """Suggested questions are tailored based on user's company status."""
    response = client.get(
        "/api/v1/chatbot/suggested-questions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # test_company is INCORPORATED so questions should be post-incorp related
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) >= 1


def test_chatbot_suggested_questions_requires_auth(client):
    """GET /chatbot/suggested-questions without auth returns 401."""
    response = client.get("/api/v1/chatbot/suggested-questions")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Copilot — POST /copilot/message
# ---------------------------------------------------------------------------


def test_copilot_message(client, test_user, auth_headers, test_company):
    """POST /copilot/message returns a context-aware response."""
    response = client.post(
        "/api/v1/copilot/message",
        json={
            "message": "Help me file",
            "company_id": test_company.id,
            "current_page": "compliance",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_copilot_message_requires_auth(client, test_company):
    """POST /copilot/message without auth returns 401."""
    response = client.post(
        "/api/v1/copilot/message",
        json={
            "message": "Help me",
            "company_id": test_company.id,
            "current_page": "compliance",
        },
    )
    assert response.status_code == 401


def test_copilot_message_wrong_company(client, test_user, auth_headers):
    """POST /copilot/message with non-owned company returns 404."""
    response = client.post(
        "/api/v1/copilot/message",
        json={
            "message": "Help me",
            "company_id": 99999,
            "current_page": "compliance",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Copilot — GET /copilot/suggestions/{company_id}
# ---------------------------------------------------------------------------


def test_copilot_suggestions(client, test_user, auth_headers, test_company):
    """GET /copilot/suggestions/{id}?page=compliance returns suggestions."""
    response = client.get(
        f"/api/v1/copilot/suggestions/{test_company.id}?page=compliance",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert "suggestion_count" in data
    assert data["suggestion_count"] == len(data["suggestions"])


def test_copilot_suggestions_default_page(
    client, test_user, auth_headers, test_company
):
    """GET /copilot/suggestions/{id} without page param uses default."""
    response = client.get(
        f"/api/v1/copilot/suggestions/{test_company.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data


def test_copilot_suggestions_requires_auth(client, test_company):
    """GET /copilot/suggestions without auth returns 401."""
    response = client.get(
        f"/api/v1/copilot/suggestions/{test_company.id}?page=compliance",
    )
    assert response.status_code == 401


def test_copilot_suggestions_wrong_company(client, test_user, auth_headers):
    """GET /copilot/suggestions for non-owned company returns 404."""
    response = client.get(
        "/api/v1/copilot/suggestions/99999?page=compliance",
        headers=auth_headers,
    )
    assert response.status_code == 404
