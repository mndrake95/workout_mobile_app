import pytest

@pytest.mark.anyio
async def test_register_user(client):
    response = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    data = response.json()
    
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["username"] == "test_user"
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert response.status_code == 201
    print(response)
    print(data)