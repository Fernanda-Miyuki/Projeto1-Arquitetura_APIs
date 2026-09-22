import os
import sys
import xml.etree.ElementTree as ET
import pytest

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from helpers_soap import build_soap_envelope, parse_soap_response


class TestContratoWSDLESchema:
    def test_wsdl_disponivel_e_status_200(self, wsgi_client):
        response = wsgi_client.get("/soap?wsdl")
        
        assert response.status_code == 200
        assert "xml" in response.content_type
        
        root = ET.fromstring(response.get_data())
        assert root.tag.endswith("definitions")

    def test_wsdl_target_namespace(self, wsgi_client):
        response = wsgi_client.get("/soap?wsdl")
        root = ET.fromstring(response.get_data())
        
        assert root.attrib.get("targetNamespace") == "http://meuzoo.com/schemas/animal"

    def test_wsdl_operacoes_declaradas(self, wsgi_client):
        response = wsgi_client.get("/soap?wsdl")
        root = ET.fromstring(response.get_data())

        operacoes = set()
        for op in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
            name = op.attrib.get("name")
            if name:
                operacoes.add(name)

        operacoes_esperadas = {
            "cadastrar_animal",
            "listar_animais",
            "buscar_animal_id",
            "deletar_animal",
        }

        assert operacoes_esperadas.issubset(operacoes), f"Operações ausentes: {operacoes_esperadas - operacoes}"

    def test_wsdl_schema_complex_type_animal(self, wsgi_client):
        response = wsgi_client.get("/soap?wsdl")
        root = ET.fromstring(response.get_data())

        complex_types = root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType")
        animal_schema_ct = None
        for ct in complex_types:
            if ct.attrib.get("name") == "AnimalSchema":
                animal_schema_ct = ct
                break

        assert animal_schema_ct is not None, "ComplexType 'AnimalSchema' não encontrado no WSDL."

        # Extrai os elementos filhos
        elementos = animal_schema_ct.findall(".//{http://www.w3.org/2001/XMLSchema}element")
        nomes_elementos = {el.attrib.get("name") for el in elementos}
        campos_esperados = {"id", "nome", "idade", "peso", "raca", "tipo"}

        assert campos_esperados.issubset(nomes_elementos), f"Campos ausentes no AnimalSchema: {campos_esperados - nomes_elementos}"

    def test_contrato_requisicao_valida_cumpre_contrato(self, wsgi_client):
        payload = build_soap_envelope(
            "tns:buscar_animal_id",
            {"tns:animal_id": 1},
        )
        response = wsgi_client.post("/soap", data=payload, content_type="text/xml; charset=utf-8")
        
        assert response.status_code == 200
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is False

    def test_contrato_rejeicao_tipo_invalido_schema_validation(self, wsgi_client):
        payload = build_soap_envelope(
            "tns:buscar_animal_id",
            {"tns:animal_id": "NAO_EH_NUMERO"},
        )
        response = wsgi_client.post("/soap", data=payload, content_type="text/xml; charset=utf-8")

        assert response.status_code == 500
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is True
        assert "SchemaValidationError" in resultado["faultcode"]
        assert "is not a valid value of the atomic type 'xs:integer'" in resultado["faultstring"]

    def test_contrato_rejeicao_xml_malformado(self, wsgi_client):
        response = wsgi_client.post("/soap", data="<corpo-invalido>", content_type="text/xml; charset=utf-8")

        assert response.status_code == 500
        resultado = parse_soap_response(response.get_data())
        assert resultado["is_fault"] is True
        assert "XMLSyntaxError" in resultado["faultcode"]
