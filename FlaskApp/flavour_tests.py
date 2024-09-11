import pytest
from flask import Flask
from MikesApi import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_ubuntu_flavour(client):
    response = client.get("/flavours/Ubuntu")
    assert response.status_code == 200
    expected_response = (
        "Distro Name: Ubuntu, Supported Versions: 24.04 Noble Numbat (LTS), 22.04 Jammy Jellyfish (LTS), End Dates: 25/04/29, 01/04/27"
    )
    assert response.data.decode('utf-8') == expected_response
    