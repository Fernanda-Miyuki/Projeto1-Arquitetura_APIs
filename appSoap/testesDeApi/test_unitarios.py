import os
import sys
from unittest.mock import patch
import pytest

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from services.animais_service import AnimaisService
from controllers.animal_controller import AnimalSOAPController
from schemas.animais_schema import AnimalSchema


class TestAnimaisService:
    def test_cadastrar_animal_com_sucesso(self, isolated_csv):
        novo = AnimaisService.cadastrar_animal("Tigre", 4, 210.5, "Bengala", "Felino")
        
        assert isinstance(novo, dict)
        assert novo["id"] == 3 
        assert novo["nome"] == "Tigre"
        assert novo["idade"] == 4
        assert novo["peso"] == 210.5
        assert novo["raca"] == "Bengala"
        assert novo["tipo"] == "Felino"

    def test_listar_animais(self, isolated_csv):
        animais = AnimaisService.listar_animais()
        
        assert isinstance(animais, list)
        assert len(animais) == 2
        assert animais[0]["id"] == 1
        assert animais[0]["nome"] == "Leao"
        assert isinstance(animais[0]["peso"], float)
        assert isinstance(animais[0]["idade"], int)
        assert animais[1]["id"] == 2
        assert animais[1]["nome"] == "Pinguim"

    def test_buscar_animal_existente(self, isolated_csv):
        animal = AnimaisService.buscar_animal(1)
        
        assert animal is not None
        assert animal["id"] == 1
        assert animal["nome"] == "Leao"
        assert animal["raca"] == "Africano"

    def test_buscar_animal_inexistente(self, isolated_csv):
        animal = AnimaisService.buscar_animal(999)
        assert animal is None

    def test_atualizar_animal_existente(self, isolated_csv):
        atualizado = AnimaisService.atualizar_animal(1, "Leao Atualizado", 6, 205.0, "Africano Real", "Felino")
        
        assert atualizado is not None
        assert atualizado["id"] == 1
        assert atualizado["nome"] == "Leao Atualizado"
        assert atualizado["idade"] == 6
        assert atualizado["peso"] == 205.0

        # Confirma persistência
        buscado = AnimaisService.buscar_animal(1)
        assert buscado is not None
        assert buscado["nome"] == "Leao Atualizado"

    def test_atualizar_animal_inexistente(self, isolated_csv):
        resultado = AnimaisService.atualizar_animal(999, "Fantasma", 1, 10.0, "N/A", "N/A")
        assert resultado is None

    def test_remover_animal_existente(self, isolated_csv):
        removido = AnimaisService.remover_animal(1)
        
        assert removido is not None
        assert removido["id"] == 1
        assert removido["nome"] == "Leao"

        # Confirma que não existe mais
        assert AnimaisService.buscar_animal(1) is None
        # Lista deve ter ficado com 1
        assert len(AnimaisService.listar_animais()) == 1

    def test_remover_animal_inexistente(self, isolated_csv):
        resultado = AnimaisService.remover_animal(999)
        assert resultado is None
        assert len(AnimaisService.listar_animais()) == 2

    def test_gerar_proximo_id_com_csv_vazio(self, empty_csv):
        proximo_id = AnimaisService._gerar_proximo_id()
        assert proximo_id == 1

    def test_gerar_proximo_id_com_registros(self, isolated_csv):
        proximo_id = AnimaisService._gerar_proximo_id()
        assert proximo_id == 3  # Registros existentes têm IDs 1 e 2


class TestAnimalSOAPController:
    """Testes unitários para o controlador AnimalSOAPController e mapeamento com schemas."""

    def test_cadastrar_animal_controller(self, isolated_csv):
        animal_schema = AnimalSOAPController.cadastrar_animal(
            None, nome="Lobo", idade=3, peso=40.0, raca="Iberico", tipo="Canideo"
        )
        
        assert isinstance(animal_schema, AnimalSchema)
        assert animal_schema.id == 3
        assert animal_schema.nome == "Lobo"
        assert animal_schema.idade == 3
        assert animal_schema.peso == 40.0
        assert animal_schema.raca == "Iberico"
        assert animal_schema.tipo == "Canideo"

    def test_listar_animais_controller(self, isolated_csv):
        lista = AnimalSOAPController.listar_animais(None)
        
        assert isinstance(lista, list)
        assert len(lista) == 2
        assert all(isinstance(item, AnimalSchema) for item in lista)
        assert lista[0].nome == "Leao"
        assert lista[1].nome == "Pinguim"

    def test_buscar_animal_id_existente(self, isolated_csv):
        resultado = AnimalSOAPController.buscar_animal_id(None, 1)
        
        assert isinstance(resultado, AnimalSchema)
        assert resultado.id == 1
        assert resultado.nome == "Leao"

    def test_buscar_animal_id_inexistente(self, isolated_csv):
        resultado = AnimalSOAPController.buscar_animal_id(None, 999)
        assert resultado is None

    def test_deletar_animal_existente(self, isolated_csv):
        resultado = AnimalSOAPController.deletar_animal(None, 1)
        
        assert isinstance(resultado, AnimalSchema)
        assert resultado.id == 1
        assert resultado.nome == "Leao"
        
        # Garante que buscar subsequente retorna None
        assert AnimalSOAPController.buscar_animal_id(None, 1) is None

    def test_deletar_animal_inexistente(self, isolated_csv):
        resultado = AnimalSOAPController.deletar_animal(None, 999)
        assert resultado is None


class TestAnimalSchema:
    """Testes unitários para a definição do ComplexModel AnimalSchema."""

    def test_schema_namespace_e_atributos(self):
        schema = AnimalSchema()
        schema.id = 10
        schema.nome = "Aguia"
        schema.idade = 4
        schema.peso = 6.5
        schema.raca = "Real"
        schema.tipo = "Ave"

        assert AnimalSchema.__namespace__ == "http://meuzoo.com/schemas/animal"
        assert schema.id == 10
        assert schema.nome == "Aguia"
        assert schema.idade == 4
        assert schema.peso == 6.5
        assert schema.raca == "Real"
        assert schema.tipo == "Ave"
