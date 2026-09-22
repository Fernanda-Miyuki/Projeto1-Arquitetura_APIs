def test_create_user_contract(client):

    response = client.post(
        "/users/",
        json={
            "name": "Contrato Teste",
            "email": "contrato@teste.com",
            "password": "12345678"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "is_active" in data
    assert "created_at" in data


    assert "password" not in data
    assert "password_hash" not in data


def test_get_user_contract(client):

    create_response = client.post(
        "/users/",
        json={
            "name": "Contrato GET",
            "email": "contratoget@teste.com",
            "password": "12345678"
        }
    )

    user_id = create_response.json()["id"]

    response = client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "id",
        "name",
        "email",
        "is_active",
        "created_at"
    }

    assert set(data.keys()) == expected_fields


def test_not_found_contract(client):

    response = client.get(
        "/users/999"
    )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data
    assert isinstance(data["detail"], str)