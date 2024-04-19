from flask import Flask
from flask_cors import CORS
from create.database import db  
def create_app():
    app = Flask(__name__, template_folder="../templates")
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Chenggou:123456@175.24.164.112:3306/haut'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 数据库初始化
    db.__init__(app)


    CORS(app, origins=" http://localhost:5173/")

    return app

