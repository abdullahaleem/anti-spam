"""
Pydantic is installed by default with fastapi and this
is how you configure your settings for fastapi.
this includes things like env variables but also
other type of configuration you want on your entire project 
e.g. if its in debug mode or not
the idea is we will have a function that will return an istance of 
settings class and we want it to be already set which is a bit
different than our machien leraning class where we did a data class and
configured it ourself.

The basesetting from pydantic will do configuration for us
base of our env variables 

"""
import os
from functools import lru_cache
from pydantic import BaseSettings, Field

os.environ["CQLENG_ALLOW_SCHEMA_MANAGEMENT"] = "1"

class Settings(BaseSettings):
    aws_access_key_id: str = None
    aws_secret_access_key:str = None
    # we can also map it without feild by making sure the variable name is name as env caps dont matter
    db_client_id: str = Field(..., env="ASTRA_DB_CLIENT_ID")
    db_client_secret: str = Field(..., env="ASTRA_DB_CLIENT_SECRET")

    class Config:
        env_file = ".env"

# caches the results of this function anywhere its called and doesn't recreate its instance
@lru_cache
def get_settings():
    return Settings()