import csv
import os

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "animais.csv")

class AnimaisService:
    @classmethod
    def _verifica_csv(cls):
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as arquivo:
                escritor_csv = csv.writer(arquivo)
                escritor_csv.writerow(['id', 'nome', 'idade', 'peso', 'raca', 'tipo'])

    @classmethod
    def _gerar_proximo_id(cls):
        cls._verifica_csv()
        max_id = 0
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for linha in leitor_csv:
                if linha['id']:
                    max_id = max(max_id, int(linha['id']))
        return max_id + 1

    @classmethod
    def cadastrar_animal(cls, nome: str, idade: int, peso: float, raca: str, tipo: str) -> dict:
        cls._verifica_csv()
        novo_id = cls._gerar_proximo_id()
        novo_animal = {
            "id": novo_id,
            "nome": nome,
            "idade": int(idade),
            "peso": float(peso),
            "raca": raca,
            "tipo": tipo
        }
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as arquivo:
            escritor_csv = csv.DictWriter(arquivo, fieldnames=['id', 'nome', 'idade', 'peso', 'raca', 'tipo'])
            escritor_csv.writerow(novo_animal)
        return novo_animal

    @classmethod
    def listar_animais(cls) -> list[dict]:
        cls._verifica_csv()
        lista_animais = []
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for linha in leitor_csv:
                lista_animais.append({
                    "id": int(linha['id']),
                    "nome": linha['nome'],
                    "idade": int(linha['idade']),
                    "peso": float(linha['peso']),
                    "raca": linha['raca'],
                    "tipo": linha['tipo']
                })
        return lista_animais

    @classmethod
    def buscar_animal(cls, animal_id: int) -> dict | None:
        cls._verifica_csv()
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for animal in leitor_csv:
                if int(animal['id']) == int(animal_id):
                    return {
                        "id": int(animal['id']),
                        "nome": animal['nome'],
                        "idade": int(animal['idade']),
                        "peso": float(animal['peso']),
                        "raca": animal['raca'],
                        "tipo": animal['tipo']
                    }
        return None

    @classmethod
    def atualizar_animal(cls, animal_id: int, nome: str, idade: int, peso: float, raca: str, tipo: str) -> dict | None:
        cls._verifica_csv()
        linhas = []
        animal_atualizado = None
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for animal in leitor_csv:
                if int(animal['id']) == int(animal_id):
                    animal['nome'] = nome
                    animal['idade'] = str(idade)
                    animal['peso'] = str(peso)
                    animal['raca'] = raca
                    animal['tipo'] = tipo
                    animal_atualizado = {
                        "id": int(animal['id']),
                        "nome": animal['nome'],
                        "idade": int(animal['idade']),
                        "peso": float(animal['peso']),
                        "raca": animal['raca'],
                        "tipo": animal['tipo']
                    }
                linhas.append(animal)
        
        if animal_atualizado:
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=['id', 'nome', 'idade', 'peso', 'raca', 'tipo'])
                escritor.writeheader()
                escritor.writerows(linhas)

        return animal_atualizado

    @classmethod
    def remover_animal(cls, animal_id: int) -> dict | None:
        cls._verifica_csv()
        linhas = []
        animal_removido = None
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for animal in leitor_csv:
                if int(animal['id']) == int(animal_id):
                    animal_removido = {
                        "id": int(animal['id']),
                        "nome": animal['nome'],
                        "idade": int(animal['idade']),
                        "peso": float(animal['peso']),
                        "raca": animal['raca'],
                        "tipo": animal['tipo']
                    }
                else:
                    linhas.append(animal)

        if animal_removido:
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=['id', 'nome', 'idade', 'peso', 'raca', 'tipo'])
                escritor.writeheader()
                escritor.writerows(linhas)

        return animal_removido
