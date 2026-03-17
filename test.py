import pytest
from unittest.mock import patch, MagicMock
from servidor import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("createadbd.connect_db")
def test_listar_imoveis_vazio(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value  = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")
    mock_cursor.fetchall.assert_called_once()


@patch("createadbd.connect_db")
def test_listar_imoveis_com_dados(mock_conectar_banco, client):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (678, "Rua A", "Rua", "Centro", "Curitiba", "81510", "apartamento", "538003", "2020-07-08"),
        (136, "Rua B", "Avenida", "Batel", "Curitiba", "58020", "casa", "955726", "2019-07-11"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200

    result = response.get_json()

    assert len(result) == 2
    assert result[0]["id"] == 678
    assert result[0]["logradouro"] == "Rua A"
    assert result[1]["id"] == 136


@patch("createadbd.connect_db")
def test_criar_imovel_ok(mock_conectar_banco, client):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 100

    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Rua das Flores",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "cep": "01310100",
        "tipo": "apartamento",
        "valor": "500000",
        "data_aquisicao": "2023-01-15"
    }

    response = client.post("/imoveis", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 100}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_criar_imovel_erro_validacao(client):

    response = client.post("/imoveis", json={"logradouro": "Rua das Flores"})

    assert response.status_code == 400
    assert "erro" in response.get_json()


@patch("createadbd.connect_db")
def test_obter_imovel_ok(mock_conectar_banco, client):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (
        678, "Rua A", "Rua", "Centro", "Curitiba",
        "81510", "apartamento", "538003", "2020-07-08"
    )

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/678")

    assert response.status_code == 200

    result = response.get_json()

    assert result["id"] == 678
    assert result["logradouro"] == "Rua A"
    assert result["tipo"] == "apartamento"

    mock_cursor.execute.assert_called_once()


@patch("createadbd.connect_db")
def test_obter_imovel_not_found(mock_conectar_banco, client):

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

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1

    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Rua Nova",
        "tipo_logradouro": "Avenida",
        "bairro": "Vila Maria",
        "cidade": "São Paulo",
        "cep": "01310100",
        "tipo": "casa",
        "valor": "600000",
        "data_aquisicao": "2023-06-20"
    }

    response = client.put("/imoveis/678", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel atualizado com sucesso"}

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("createadbd.connect_db")
def test_atualizar_imovel_not_found(mock_conectar_banco, client):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 0

    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Rua Nova",
        "tipo_logradouro": "Avenida",
        "bairro": "Vila Maria",
        "cidade": "São Paulo",
        "cep": "01310100",
        "tipo": "casa",
        "valor": "600000",
        "data_aquisicao": "2023-06-20"
    }

    response = client.put("/imoveis/999", json=payload)

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@patch("createadbd.connect_db")
def test_deletar_imovel_ok(mock_conectar_banco, client):

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

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 0

    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@patch("createadbd.connect_db")
def test_listar_imoveis_por_cidade(mock_conectar_banco, client):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn

    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, "Rua C", "Rua", "Centro", "Curitiba", "80000", "casa", "500000", "2020-01-01"),
    ]

    response = client.get("/imoveis?cidade=Curitiba")

    result = response.get_json()
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s",
        ("Curitiba",)
    )

    mock_cursor.fetchall.assert_called_once()

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]["cidade"] == "Curitiba"


@patch("createadbd.connect_db")
def test_listar_imoveis_por_tipo(mock_conectar_banco, client):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn

    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, "Rua A", "Rua", "Centro", "Curitiba", "80000", "casa", "500000", "2020-01-01"),
    ]

    response = client.get("/imoveis?tipo=casa")

    result = response.get_json()
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s",
        ("casa",)
    )

    mock_cursor.fetchall.assert_called_once()

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]["tipo"] == "casa"
    