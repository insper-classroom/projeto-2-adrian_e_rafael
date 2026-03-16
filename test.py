import pytest
from unittest.mock import patch, MagicMock
from servidor import app


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("createadbd.connect_db")
def test_listar_imoveis_vazio(mock_conectar_banco, client):
    """GET / - lista vazia de imóveis."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Nenhum imovel encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "SELECT * from imoveis"
    )
    mock_cursor.fetchall.assert_called_once()


@patch("createadbd.connect_db")
def test_listar_imoveis_com_dados(mock_conectar_banco, client):
    """GET /imoveis - lista com dados de imóveis."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (678, "Andrew Rest", "Alameda", "Davidville", "Erinbury", "81510", "apartamento", "538003", "2020-07-08"),
        (136, "Angela Burg", "Rua", "North Jennifer", "South Kenneth", "58020", "casa", "955726", "2019-07-11"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    result = response.get_json()
    assert "imoveis" in result
    assert len(result["imoveis"]) == 2
    assert result["imoveis"][0]["id"] == 678
    assert result["imoveis"][0]["nome"] == "Andrew Rest"
    assert result["imoveis"][1]["id"] == 136

    mock_cursor.execute.assert_called_once_with(
        "SELECT * from imoveis"
    )
    mock_cursor.fetchall.assert_called_once()



@patch("createadbd.connect_db")
def test_criar_imovel_ok(mock_conectar_banco, client):
    """POST /imoveis - cria imóvel com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simula ID gerado pelo banco
    mock_cursor.lastrowid = 100

    mock_conectar_banco.return_value = mock_conn

    payload = {
        'logradouro': "Rua das Flores",
        'tipo_logradouro': "Rua",
        'bairro': "Centro",
        'cidade': "São Paulo",
        'cep': '01310100',
        'tipo': 'apartamento',
        'valor': '500000',
        'data_aquisicao': '2023-01-15'
    }

    response = client.post("/imoveis", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 100}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("createadbd.connect_db")
def test_criar_imovel_erro_validacao(mock_conectar_banco, client):
    """POST /imoveis - falta campo obrigatório -> 400."""
    response = client.post("/imoveis", json={"logradouro": "Rua das Flores"})

    assert response.status_code == 400
    assert "erro" in response.get_json()

    mock_conectar_banco.assert_not_called()


@patch("createadbd.connect_db")
def test_obter_imovel_ok(mock_conectar_banco, client):
    """GET /imoveis/<id> - imóvel existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (
        678, "Andrew Rest", "Alameda", "Davidville", "Erinbury", 
        "81510", "apartamento", "538003", "2020-07-08"
    )
    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/678")

    assert response.status_code == 200
    result = response.get_json()
    assert result["id"] == 678
    assert result["nome"] == "Andrew Rest"
    assert result["tipo"] == "apartamento"

    mock_cursor.execute.assert_called_once()


@patch("createadbd.connect_db")
def test_obter_imovel_not_found(mock_conectar_banco, client):
    """GET /imoveis/<id> - imóvel não existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None
    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@patch("createadbd.connect_db")
def test_atualizar_imovel_ok(mock_conectar_banco, client):
    """PUT /imoveis/<id> - atualiza com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    payload = {
        'logradouro': "Rua Nova",
        'tipo_logradouro': "Avenida",
        'bairro': "Vila Maria",
        'cidade': "São Paulo",
        'cep': '01310100',
        'tipo': 'casa',
        'valor': '600000',
        'data_aquisicao': '2023-06-20'
    }
    response = client.put("/imoveis/678", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel atualizado com sucesso"}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("createadbd.connect_db")
def test_atualizar_imovel_not_found(mock_conectar_banco, client):
    """PUT /imoveis/<id> - imóvel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    payload = {
        'logradouro': "Rua Nova",
        'tipo_logradouro': "Avenida",
        'bairro': "Vila Maria",
        'cidade': "São Paulo",
        'cep': '01310100',
        'tipo': 'casa',
        'valor': '600000',
        'data_aquisicao': '2023-06-20'
    }
    response = client.put("/imoveis/999", json=payload)

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@patch("createadbd.connect_db")
def test_deletar_imovel_ok(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - deleta com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/678")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel excluído com sucesso"}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("createadbd.connect_db")
def test_deletar_imovel_not_found(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - imóvel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}
