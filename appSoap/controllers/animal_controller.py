from spyne import ServiceBase, rpc, Integer, Unicode, Float, Array
from schemas.animais_schema import AnimalSchema
from services.animais_service import AnimaisService

class AnimalSOAPController(ServiceBase):

    @rpc(Unicode, Integer, Float, Unicode, Unicode, _returns=AnimalSchema)
    def cadastrar_animal(ctx, nome: str, idade: int, peso: float, raca: str, tipo: str):
        dados = AnimaisService.cadastrar_animal(nome, idade, peso, raca, tipo)
         
        animal = AnimalSchema()
        animal.id = dados["id"]
        animal.nome = dados["nome"]
        animal.idade = dados["idade"]
        animal.peso = dados["peso"]
        animal.raca = dados["raca"]
        animal.tipo = dados["tipo"]
        
        return animal

    @rpc(_returns=Array(AnimalSchema))
    def listar_animais(ctx):
        dados = AnimaisService.listar_animais()
        
        lista_animais = []
        for item in dados:
            animal = AnimalSchema()
            animal.id = item["id"]
            animal.nome = item["nome"]
            animal.idade = item["idade"]
            animal.peso = item["peso"]
            animal.raca = item["raca"]
            animal.tipo = item["tipo"]
            lista_animais.append(animal)
        
        return lista_animais

    @rpc(Integer, _returns=AnimalSchema)
    def buscar_animal_id(ctx, animal_id: int):
        dados = AnimaisService.buscar_animal(animal_id)
        if not dados:
            return None

        animal = AnimalSchema()
        animal.id = dados["id"]
        animal.nome = dados["nome"]
        animal.idade = dados["idade"]
        animal.peso = dados["peso"]
        animal.raca = dados["raca"]
        animal.tipo = dados["tipo"]
        
        return animal
    
    @rpc(Integer, _returns=AnimalSchema)
    def deletar_animal(ctx, animal_id: int):
        dados = AnimaisService.remover_animal(animal_id)
        if not dados:
            return None

        animal = AnimalSchema()
        animal.id = dados["id"]
        animal.nome = dados["nome"]
        animal.idade = dados["idade"]
        animal.peso = dados["peso"]
        animal.raca = dados["raca"]
        animal.tipo = dados["tipo"]
        
        return animal
        
    
        
