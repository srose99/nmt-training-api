import pytest, logging
from flask import Flask
from unittest.mock import patch
from MikesApi import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test flavours endpoint for a specific entry
def test_get_ubuntu_flavour(client):
    response = client.get("/flavours/Ubuntu")
    assert response.status_code == 200
    expected_response = (
        "Distro Name: Ubuntu, Supported Versions: 24.04 Noble Numbat (LTS), 22.04 Jammy Jellyfish (LTS), End Dates: 25/04/29, 01/04/27"
    )
    assert response.data.decode('utf-8') == expected_response

# Tests post by making a get after post to confirm data has been added
def test_post_new_linux_distro(client):
    new_distro = {
        "name": "Fedora",
        "supported_versions": [
            {
                "version": "34",
                "release_date": "27/04/21",
                "end_date": "29/04/22"
            },
            {
                "version": "33",
                "release_date": "27/10/20",
                "end_date": "30/11/21"
            }
        ]
    }

    response = client.post("/", json=new_distro)
    assert response.status_code == 201
    assert response.json["message"] == "Linux distribution added successfully"

    response = client.get("/")
    assert response.status_code == 200
    assert any(distro['name'] == "Fedora" for distro in response.json)

# Tests for specific metrics within metrics endpoint
def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"number_of_requests" in response.data
    assert b"request_latency_seconds" in response.data

# Tests test logger for the correct logging schema being used
def test_logging(client):
    with patch('MikesApi.logger') as mock_logger:
        client.get("/flavours/Ubuntu")
        mock_logger.info.assert_called_with('Successful request for Ubuntu')