
from spyne import ComplexModel, Integer, Float, Unicode

class AnimalSchema(ComplexModel):  # type: ignore
    __namespace__ = "http://meuzoo.com/schemas/animal"
    id = Integer
    nome =  Unicode
    idade = Integer
    peso = Float
    raca = Unicode
    tipo = Unicode
