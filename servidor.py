from flask import Flask, request,jsonify
import os 
from createadbd import close_db,connect_db
from dotenv import load_dotenv

load_dotenv('.env')


def criar_app():
    

    app = Flask(__name__, instance_relative_config= True)
    
    app.teardown_appcontext(close_db)

    app.config.from_mapping(
        secret_key = os.environ.get('SECRET_KEY')
    )

    return app


app = criar_app()

@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    conexao = connect_db()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM imoveis")

    rows = cursor.fetchall()


    imoveis = [
        {
            "id": id_imovel,
            "logradouro": logradouro,
            "tipo_logradouro": tipo_logradouro,
            "bairro": bairro,
            "cidade": cidade_item,
            "cep": cep,
            "tipo": tipo_item,
            "valor": valor,
            "data_aquisicao": data,
        }
        for id_imovel, logradouro, tipo_logradouro, bairro, cidade_item, cep, tipo_item, valor, data in rows
    ]

    return jsonify(imoveis)

@app.route('/imoveis', methods=['POST'])
def criar_imovel():
    dados = request.get_json(silent=True)
    if dados is None:
        return jsonify({"erro": "JSON inválido"}), 400
    lista = ["logradouro", "tipo_logradouro", "bairro",'cidade','cep','tipo','valor','data_aquisicao']
    for x in lista:
        if x not in dados:
            return jsonify({"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro,cidade,cep,tipo,valor,data_aquisicao"}), 400
    conexao = connect_db()
    cursor = conexao.cursor()

    cursor.execute(
        'INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (dados['logradouro'], dados['tipo_logradouro'], dados['bairro'], dados['cidade'], dados['cep'], dados['tipo'], dados['valor'], dados['data_aquisicao'])
        )
    conexao.commit()
    id_novo = cursor.lastrowid
    return jsonify({"id": id_novo}), 201

# GET /imoveis/<id>: Retorna um imóvel específico pelo ID.
@app.route('/imoveis/<int:id>', methods=['GET'])
def obter_imovel(id):
    conexao = connect_db()
    cursor = conexao.cursor()

    cursor.execute("SELECT id_imovel, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE id_imovel = %s", (id,))
    resultado = cursor.fetchone()



    if resultado is None:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    id_imovel, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao = resultado
    
    imovel = {
        "id": id_imovel,
        "logradouro": logradouro,
        "tipo_logradouro": tipo_logradouro,
        "bairro": bairro,
        "cidade": cidade,
        "cep": cep,
        "tipo": tipo,
        "valor": valor,
        "data_aquisicao": data_aquisicao
    }
    return jsonify(imovel)

# PUT /imoveis/<id>: Atualiza um imóvel específico.
@app.route('/imoveis/<int:id>', methods=['PUT'])
def atualizar_imovel(id):

    dados = request.get_json()
    lista = ["logradouro", "tipo_logradouro", "bairro",'cidade','cep','tipo','valor','data_aquisicao']
    for x in lista:
        if x not in dados:
            return jsonify({"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro,cidade,cep,tipo,valor,data_aquisicao"}), 400

    conexao = connect_db()
    cursor = conexao.cursor()

    cursor.execute("UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id_imovel = %s", (dados['logradouro'], dados['tipo_logradouro'], dados['bairro'], dados['cidade'], dados['cep'], dados['tipo'], dados['valor'], dados['data_aquisicao'], id))
    conexao.commit()


    linhas_mod = cursor.rowcount
    if linhas_mod == 0:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return '', 204

# DELETE /imoveis/<id>: Deleta um imóvel específico.
@app.route('/imoveis/<int:id>', methods=['DELETE'])
def deletar_imovel(id):

    conexao = connect_db()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM imoveis WHERE id_imovel = %s", (id,))
    conexao.commit()

    linhas_mod = cursor.rowcount
    if linhas_mod == 0:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return jsonify({"mensagem": "Imóvel excluído com sucesso"})

# Lista por tipo (apartamento, terreno, apartamento, etc) com todos os atributos
@app.route('/imoveis/tipo/<string:tipo>', methods=['GET']) 
def listar_imoveis_por_tipo(tipo):
    conexao = connect_db()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM imoveis WHERE tipo = %s", (tipo,))
    rows = cursor.fetchall()
    imoveis = [
        {
            "id": id_imovel,
            "logradouro": logradouro,
            "tipo_logradouro": tipo_logradouro,
            "bairro": bairro,
            "cidade": cidade_item,
            "cep": cep,
            "tipo": tipo_item,
            "valor": valor,
            "data_aquisicao": data,
        }
        for id_imovel, logradouro, tipo_logradouro, bairro, cidade_item, cep, tipo_item, valor, data in rows
    ]
    return jsonify(imoveis)

# Lista por cidade com todos os atributos
@app.route('/imoveis/cidade/<string:cidade>', methods=['GET']) 
def listar_imoveis_por_cidade(cidade):
    conexao = connect_db()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM imoveis WHERE cidade = %s", (cidade,))
    rows = cursor.fetchall()
    imoveis = [
        {
            "id": id_imovel,
            "logradouro": logradouro,
            "tipo_logradouro": tipo_logradouro,
            "bairro": bairro,
            "cidade": cidade_item,
            "cep": cep,
            "tipo": tipo_item,
            "valor": valor,
            "data_aquisicao": data,
        }
        for id_imovel, logradouro, tipo_logradouro, bairro, cidade_item, cep, tipo_item, valor, data in rows
    ]
    return jsonify(imoveis)

if __name__ == '__main__':
    app.run(debug=True)


