from flask import Flask, request,jsonify
import os 
from createadbd import close_db,connect_db


def criar_app():
    

    app = Flask(__name__, instance_relative_config= True)
    
    app.teardown_appcontext(close_db)

    app.config.from_mapping(
        secret_key = os.environ['SECRET_KEY']
    )


    return app


app = criar_app()


if __name__ == '__main__':
    app.run(debug=True)

