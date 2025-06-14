import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_chat_endpoint(client):
    response = client.post("/chat", json={"user_input": "bạn là ai"})
    assert response.status_code == 200
    
def test_chat_endpoint_2(client):
    response = client.post("/chat", json={"user_input": "tôi muốn đổi chuyến bay"})
    assert response.status_code == 200
    
def test_chat_endpoint_3(client):
    response = client.post("/chat", json={"user_input": "tôi muốn dời xuống 6 giờ"})
    assert response.status_code == 200

def test_vector_query(client):
    response = client.post("/vector/query", json={
        "user_input": "mua vé máy bay ở đâu",
        "num": 5
    })
    assert response.status_code == 200

def test_image_upload(client):
    with open("test_image.png", "rb") as img:
        data = {
            "file": (img, "test_image.png"),
            "user_input": "có lây không",
        }
        response = client.post("/image", data=data, content_type='multipart/form-data', buffered=False)
    assert response.status_code == 200
