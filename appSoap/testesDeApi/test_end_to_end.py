import os
import sys
import requests
import pytest

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from helpers_soap import build_soap_envelope, parse_soap_response


class TestEndToEndSOAP:
    def test_e2e_descoberta_servico_e_wsdl(self, live_server):
        # 1. Checa a rota de status da API (Flask)
        res_info = requests.get(f"{live_server}/")
        assert res_info.status_code == 200
        dados_json = res_info.json()
        assert dados_json["status"] == "ON"
        assert dados_json["servico"] == "API SOAP de Cadastro de Animais"
        assert "wsdl" in dados_json

        # 2. Checa a disponibilidade do contrato WSDL via HTTP real
        res_wsdl = requests.get(f"{live_server}/soap?wsdl")
        assert res_wsdl.status_code == 200
        assert "xml" in res_wsdl.headers.get("Content-Type", "")
        assert b"definitions" in res_wsdl.content

    def test_e2e_ciclo_de_vida_completo_animal(self, live_server):
        endpoint_soap = f"{live_server}/soap"
        headers = {"Content-Type": "text/xml; charset=utf-8"}

        # --- Passo 1: Cadastrar Animal ---
        payload_cadastro = build_soap_envelope(
            "tns:cadastrar_animal",
            {
                "tns:nome": "Bidu",
                "tns:idade": 2,
                "tns:peso": 8.5,
                "tns:raca": "Schnauzer",
                "tns:tipo": "Cachorro",
            },
        )
        res_cadastro = requests.post(endpoint_soap, data=payload_cadastro, headers=headers)
        assert res_cadastro.status_code == 200

        dados_cadastro = parse_soap_response(res_cadastro.content)
        assert dados_cadastro["is_fault"] is False
        animal_criado = dados_cadastro["animal"]
        assert animal_criado is not None
        assert animal_criado["nome"] == "Bidu"
        assert animal_criado["idade"] == 2
        assert animal_criado["peso"] == 8.5
        assert animal_criado["raca"] == "Schnauzer"
        assert animal_criado["tipo"] == "Cachorro"
        novo_id = animal_criado["id"]
        assert novo_id is not None

        # --- Passo 2: Listar Animais ---
        payload_listar = build_soap_envelope("tns:listar_animais")
        res_listar = requests.post(endpoint_soap, data=payload_listar, headers=headers)
        assert res_listar.status_code == 200

        dados_listar = parse_soap_response(res_listar.content)
        assert dados_listar["is_fault"] is False
        lista_animais = dados_listar["animais"]
        # Inicialmente tínhamos 2 no isolated_csv, com o novo devemos ter 3
        assert len(lista_animais) == 3
        ids_presentes = [a["id"] for a in lista_animais]
        assert novo_id in ids_presentes

        # --- Passo 3: Buscar Animal por ID ---
        payload_buscar = build_soap_envelope(
            "tns:buscar_animal_id",
            {"tns:animal_id": novo_id},
        )
        res_buscar = requests.post(endpoint_soap, data=payload_buscar, headers=headers)
        assert res_buscar.status_code == 200

        dados_buscar = parse_soap_response(res_buscar.content)
        assert dados_buscar["is_fault"] is False
        animal_buscado = dados_buscar["animal"]
        assert animal_buscado is not None
        assert animal_buscado["id"] == novo_id
        assert animal_buscado["nome"] == "Bidu"

        # --- Passo 4: Deletar Animal por ID ---
        payload_deletar = build_soap_envelope(
            "tns:deletar_animal",
            {"tns:animal_id": novo_id},
        )
        res_deletar = requests.post(endpoint_soap, data=payload_deletar, headers=headers)
        assert res_deletar.status_code == 200

        dados_deletar = parse_soap_response(res_deletar.content)
        assert dados_deletar["is_fault"] is False
        animal_deletado = dados_deletar["animal"]
        assert animal_deletado is not None
        assert animal_deletado["id"] == novo_id
        assert animal_deletado["nome"] == "Bidu"

        # --- Passo 5: Verificar que o Animal não é mais encontrado ---
        res_buscar_pos = requests.post(endpoint_soap, data=payload_buscar, headers=headers)
        assert res_buscar_pos.status_code == 200
        dados_buscar_pos = parse_soap_response(res_buscar_pos.content)
        assert dados_buscar_pos["is_fault"] is False
        assert dados_buscar_pos["animal"] is None

        # --- Passo 6: Listar novamente e confirmar retorno ao tamanho original ---
        res_listar_pos = requests.post(endpoint_soap, data=payload_listar, headers=headers)
        assert res_listar_pos.status_code == 200
        dados_listar_pos = parse_soap_response(res_listar_pos.content)
        assert len(dados_listar_pos["animais"]) == 2
        ids_finais = [a["id"] for a in dados_listar_pos["animais"]]
        assert novo_id not in ids_finais

    def test_e2e_resiliencia_e_fault_sem_derrubar_servidor(self, live_server):
        endpoint_soap = f"{live_server}/soap"
        headers = {"Content-Type": "text/xml; charset=utf-8"}

        # Envia requisição com violação contratual de tipo
        payload_invalido = build_soap_envelope(
            "tns:buscar_animal_id",
            {"tns:animal_id": "VALOR_INVALIDO"},
        )
        res_falha = requests.post(endpoint_soap, data=payload_invalido, headers=headers)
        assert res_falha.status_code == 500

        dados_falha = parse_soap_response(res_falha.content)
        assert dados_falha["is_fault"] is True
        assert "SchemaValidationError" in dados_falha["faultcode"]

        # Verifica se o servidor continua funcionando normalmente após a falha
        res_saudavel = requests.get(f"{live_server}/")
        assert res_saudavel.status_code == 200
        assert res_saudavel.json()["status"] == "ON"
