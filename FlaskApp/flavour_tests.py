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
    assert response.json == {
        "name": "Ubuntu",
        "supported_versions": [
            {
                "version": "24.04 Noble Numbat (LTS)",
                "release_date": "25/04/24",
                "end_date": "25/04/29"
            },
            {
                "version": "22.04 Jammy Jellyfish (LTS)",
                "release_date": "21/04/22",
                "end_date": "01/04/27"
            },
        ]
    }