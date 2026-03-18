from flask import Flask, request,g
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


load_dotenv('.env')

config = {
    'host': os.getenv('DB_HOST', 'localhost'),  # Obtém o host do banco de dados da variável de ambiente
    'user': os.getenv('DB_USER'),  # Obtém o usuário do banco de dados da variável de ambiente
    'password': os.getenv('DB_PASSWORD'),  # Obtém a senha do banco de dados da variável de ambiente
    'database': os.getenv('DB_NAME', 'db_escola'),  # Obtém o nome do banco de dados da variável de ambiente
    'port': int(os.getenv('DB_PORT', 3306)),  # Obtém a porta do banco de dados da variável de ambiente
}

# Adiciona SSL apenas se o arquivo de certificado existir
ssl_ca_path = os.getenv('SSL_CA_PATH')
if ssl_ca_path and os.path.exists(ssl_ca_path):
    config['ssl_ca'] = ssl_ca_path
else:
    config['ssl_disabled'] = True  # Desabilita SSL se o certificado não existir

def connect_db():
    """Estabelece a conexão com o banco de dados usando as configurações fornecidas."""
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():

           g.conn = conn
        return conn
    except Error as err:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Erro ao conectar: {err}")
        return None
    



def close_db(error=None):
    conn = getattr(g, 'conn', None)
    if conn is not None:
        conn.close()