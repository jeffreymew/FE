import os

from setup import basedir


class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgres://postgres@standup-db:Password123!@standup-db.postgres.database.azure.com:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

