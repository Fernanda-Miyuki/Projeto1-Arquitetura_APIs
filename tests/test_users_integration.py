def test_create_user_integration(client):

    response = client.post(
        "/users/",
        json={
            "name": "Fernanda Teste",
            "email": "fernanda@teste.com",
            "password": "12345678"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Fernanda Teste"
    assert data["email"] == "fernanda@teste.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_get_users_integration(client):

    client.post(
        "/users/",
        json={
            "name": "João Teste",
            "email": "joao@teste.com",
            "password": "12345678"
        }
    )

    response = client.get("/users/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "joao@teste.com"


def test_get_user_not_found(client):

    response = client.get("/users/999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Usuário não encontrado."

def test_update_user_integration(client):

    create_response = client.post(
        "/users/",
        json={
            "name": "Nome Original",
            "email": "original@teste.com",
            "password": "12345678"
        }
    )

    user_id = create_response.json()["id"]

    response = client.put(
        f"/users/{user_id}",
        json={
            "name": "Nome Atualizado",
            "email": "atualizado@teste.com",
            "password": "novaSenha123",
            "is_active": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Nome Atualizado"
    assert data["email"] == "atualizado@teste.com"
    assert "password" not in data


def test_delete_user_integration(client):

    create_response = client.post(
        "/users/",
        json={
            "name": "Usuário Delete",
            "email": "delete@teste.com",
            "password": "12345678"
        }
    )

    user_id = create_response.json()["id"]

    response = client.delete(
        f"/users/{user_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/users/{user_id}"
    )

    assert get_response.status_code == 404