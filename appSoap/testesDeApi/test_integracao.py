import os
import sys
import pytest

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from helpers_soap import build_soap_envelope, parse_soap_response
from services.animais_service import AnimaisService


class TestIntegracaoSOAP:
    def test_soap_cadastrar_animal_integrado(self, wsgi_client):
        # 1. Monta o envelope SOAP para cadastrar_animal
        payload = build_soap_envelope(
            "tns:cadastrar_animal",
            {
                "tns:nome": "Elefante",
                "tns:idade": 12,
                "tns:peso": 3500.5,
                "tns:raca": "Africano",
                "tns:tipo": "Mamifero",
            },
        )

        # 2. Envia a requisição POST para a rota /soap
        response = wsgi_client.post(
            "/soap",
            data=payload,
            content_type="text/xml; charset=utf-8",
        )

        assert response.status_code == 200

        # 3. Faz parse da resposta XML
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False
        animal = resultado["animal"]
        assert animal is not None
        assert animal["id"] == 3
        assert animal["nome"] == "Elefante"
        assert animal["idade"] == 12
        assert animal["peso"] == 3500.5
        assert animal["raca"] == "Africano"
        assert animal["tipo"] == "Mamifero"

        # 4. Verifica se os dados foram realmente persistidos no arquivo CSV
        persistido = AnimaisService.buscar_animal(3)
        assert persistido is not None
        assert persistido["nome"] == "Elefante"

    def test_soap_listar_animais_integrado(self, wsgi_client):
        payload = build_soap_envelope("tns:listar_animais")

        response = wsgi_client.post(
            "/soap",
            data=payload,
            content_type="text/xml; charset=utf-8",
        )

        assert response.status_code == 200
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False
        animais = resultado["animais"]
        assert len(animais) == 2
        assert animais[0]["nome"] == "Leao"
        assert animais[1]["nome"] == "Pinguim"

    def test_soap_buscar_animal_id_existente_integrado(self, wsgi_client):
        payload = build_soap_envelope(
            "tns:buscar_animal_id",
            {"tns:animal_id": 1},
        )

        response = wsgi_client.post(
            "/soap",
            data=payload,
            content_type="text/xml; charset=utf-8",
        )

        assert response.status_code == 200
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False
        assert resultado["animal"] is not None
        assert resultado["animal"]["id"] == 1
        assert resultado["animal"]["nome"] == "Leao"

    def test_soap_buscar_animal_id_inexistente_integrado(self, wsgi_client):
        payload = build_soap_envelope(
            "tns:buscar_animal_id",
            {"tns:animal_id": 999},
        )

        response = wsgi_client.post(
            "/soap",
            data=payload,
            content_type="text/xml; charset=utf-8",
        )

        assert response.status_code == 200
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False
        assert resultado["animal"] is None

    def test_soap_deletar_animal_existente_integrado(self, wsgi_client):
        payload = build_soap_envelope(
            "tns:deletar_animal",
            {"tns:animal_id": 2},
        )

        response = wsgi_client.post(
            "/soap",
            data=payload,
            content_type="text/xml; charset=utf-8",
        )

        assert response.status_code == 200
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False
        assert resultado["animal"] is not None
        assert resultado["animal"]["id"] == 2
        assert resultado["animal"]["nome"] == "Pinguim"

        # Confirma que foi removido da persistência CSV
        assert AnimaisService.buscar_animal(2) is None

    def test_soap_deletar_animal_inexistente_integrado(self, wsgi_client):
        payload = build_soap_envelope(
            "tns:deletar_animal",
            {"tns:animal_id": 888},
        )

        response = wsgi_client.post(
            "/soap",
            data=payload,
            content_type="text/xml; charset=utf-8",
        )

        assert response.status_code == 200
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False
        assert resultado["animal"] is None
