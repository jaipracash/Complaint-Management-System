import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://jai:admin123@localhost/common_contributions_tracker"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
