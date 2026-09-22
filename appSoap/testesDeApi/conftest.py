import os
import sys
import tempfile
import threading
import pytest
from werkzeug.serving import make_server
from werkzeug.test import Client
from werkzeug.wrappers import Response

# Garante que a pasta appSoap esteja no sys.path
APP_SOAP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TESTS_DIR = os.path.abspath(os.path.dirname(__file__))

if APP_SOAP_DIR not in sys.path:
    sys.path.insert(0, APP_SOAP_DIR)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

import services.animais_service as animais_service_module
from app import app_composta

INITIAL_CSV_CONTENT = (
    "id,nome,idade,peso,raca,tipo\n"
    "1,Leao,5,190.5,Africano,Felino\n"
    "2,Pinguim,2,14.2,Imperador,Ave\n"
)


@pytest.fixture
def isolated_csv(monkeypatch):
    """
    Cria um arquivo CSV temporário com dados iniciais de teste e
    redireciona o AnimaisService para usá-lo durante o teste.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv", encoding="utf-8") as temp_file:
        temp_file.write(INITIAL_CSV_CONTENT)
        temp_path = temp_file.name

    monkeypatch.setattr(animais_service_module, "CSV_FILE", temp_path)

    try:
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@pytest.fixture
def empty_csv(monkeypatch):
    """
    Cria um arquivo CSV temporário apenas com o cabeçalho.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv", encoding="utf-8") as temp_file:
        temp_file.write("id,nome,idade,peso,raca,tipo\n")
        temp_path = temp_file.name

    monkeypatch.setattr(animais_service_module, "CSV_FILE", temp_path)

    try:
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@pytest.fixture
def wsgi_client(isolated_csv):
    """
    Cliente de teste WSGI da Werkzeug configurado com CSV isolado.
    """
    return Client(app_composta, Response)


@pytest.fixture(scope="function")
def live_server(isolated_csv):
    """
    Inicia o servidor WSGI em uma porta dinâmica em segundo plano para testes E2E reais via HTTP.
    """
    server = make_server("127.0.0.1", 0, app_composta)
    port = server.server_port
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"
    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
