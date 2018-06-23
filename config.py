class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE = 'rewords.db'
    SECRET_KEY = 'YmFzZWVzYWIK'

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True