import xml.etree.ElementTree as ET

SOAP_ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"
TNS_NS = "http://meuzoo.com/schemas/animal"

NAMESPACES = {
    "soapenv": SOAP_ENV_NS,
    "soap11env": SOAP_ENV_NS,
    "tns": TNS_NS,
}

def build_soap_envelope(method_name: str, params: dict | None = None, namespace: str = TNS_NS) -> str:
    """
    Constrói um envelope SOAP 1.1 com a operação e parâmetros informados.
    """
    params_xml = ""
    if params:
        for key, value in params.items():
            if value is not None:
                params_xml += f"<{key}>{value}</{key}>\n"

    if params_xml:
        inner_content = f"<{method_name}>\n{params_xml}</{method_name}>"
    else:
        inner_content = f"<{method_name}/>"

    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="{SOAP_ENV_NS}" xmlns:tns="{namespace}">
  <soapenv:Header/>
  <soapenv:Body>
    {inner_content}
  </soapenv:Body>
</soapenv:Envelope>"""
    return envelope


def parse_animal_element(elem: ET.Element) -> dict:
    """
    Converte um elemento XML <AnimalSchema> ou <*Result> em um dicionário Python com tipos convertidos.
    """
    dados = {}
    for child in elem:
        tag_name = child.tag.split("}")[-1]  # remove namespace se houver
        dados[tag_name] = child.text

    return {
        "id": int(dados["id"]) if dados.get("id") is not None else None,
        "nome": dados.get("nome"),
        "idade": int(dados["idade"]) if dados.get("idade") is not None else None,
        "peso": float(dados["peso"]) if dados.get("peso") is not None else None,
        "raca": dados.get("raca"),
        "tipo": dados.get("tipo"),
    }


def parse_soap_response(xml_bytes_or_str: bytes | str) -> dict:
    """
    Analisa a resposta XML do SOAP, identificando Faults ou extraindo os resultados.
    """
    if isinstance(xml_bytes_or_str, bytes):
        xml_str = xml_bytes_or_str.decode("utf-8")
    else:
        xml_str = xml_bytes_or_str

    root = ET.fromstring(xml_str)

    # 1. Verifica se há Fault
    fault = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
    if fault is not None:
        faultcode_el = fault.find("faultcode")
        faultstring_el = fault.find("faultstring")
        return {
            "is_fault": True,
            "faultcode": faultcode_el.text if faultcode_el is not None else "",
            "faultstring": faultstring_el.text if faultstring_el is not None else "",
            "raw": xml_str,
        }

    # 2. Verifica se há lista de elementos <AnimalSchema> (ex: listar_animais)
    animais_elements = root.findall(".//{http://meuzoo.com/schemas/animal}AnimalSchema")
    if animais_elements:
        animais = [parse_animal_element(el) for el in animais_elements]
        return {
            "is_fault": False,
            "animais": animais,
            "animal": animais[0] if len(animais) == 1 else None,
            "raw": xml_str,
        }

    # 3. Verifica se há resultado único com tag terminada em 'Result' (ex: cadastrar_animalResult)
    body = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")
    if body is not None:
        for child in body.iter():
            if child.tag.endswith("Result") and len(child) > 0:
                animal = parse_animal_element(child)
                return {
                    "is_fault": False,
                    "animais": [animal],
                    "animal": animal,
                    "raw": xml_str,
                }

    # 4. Caso não encontre nenhum registro (ex: animal inexistente)
    return {
        "is_fault": False,
        "animais": [],
        "animal": None,
        "raw": xml_str,
    }
