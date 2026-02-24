

async def register_and_login_scenario(client, username, email, password="test_password"):
    create = await client.post("/users/register", json={"username": username, 
                                                          "email": email, 
                                                          "password": password})
    create_data = create.json()

    login = await client.post("/users/login", json={"username": create_data["username"],
                                                    "password": password})
    login_data = login.json()

    return create_data, login_data
