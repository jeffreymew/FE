import os

from setup import basedir


class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgres://postgres@standup-db:Password123!@standup-db.postgres.database.azure.com:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(object):
    """Development configuration."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG_TB_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
