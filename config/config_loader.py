import re

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import List, Dict, Any, Tuple, Union


# Define your existing data models
class BaseUrlConfig(BaseModel):
    url: str
    unwanted_urls: List[str] = []
    max_threads: int = Field(default=5)
    task_class: str


class SettingsConfig(BaseModel):
    start_date: Tuple[int, int, int]
    concurrency: int
    base_urls: List[BaseUrlConfig]


class TaskConfig(BaseModel):
    task_name: str
    task_class: str
    task_type: str
    active: bool
    persist: bool = Field(default=True)
    publish: bool = Field(default=True)
    props: Dict[str, Any] = Field(default_factory=dict)

    # Dynamically generated attributes
    schema_file: str = None
    message_topic: str = None
    repository_name: str = None

    @model_validator(mode="before")
    def set_dynamic_attributes(cls, values):
        task_name = values.get('task_name')
        base_name = to_snake_case(task_name)
        values['schema_file'] = f"{base_name}"
        values['message_topic'] = f"{base_name}_topic"
        values['repository_name'] = f"{base_name}_repository"
        return values
class MongoDBConfig(BaseModel):
    db_name: str
    db_address: str


class MySQLConfig(BaseModel):
    db_name: str
    db_address: str
    user: str
    password: str


class DataBaseConfig(BaseModel):
    db_type: str = Field(..., enum=["mongo", "mysql"])
    config: Dict[str, Any]

    @model_validator(mode='before')
    def validate_db_config(cls, values):
        db_type = values.get("db_type")
        config = values.get("config")

        if db_type == "mongo":
            if "MongoDB" not in config or not isinstance(config["MongoDB"], dict):
                raise ValueError("db_type is 'mongo', but no valid MongoDBConfig found.")
            values["config"]["MongoDB"] = MongoDBConfig(**config["MongoDB"])
        elif db_type == "mysql":
            if "MySQL" not in config or not isinstance(config["MySQL"], dict):
                raise ValueError("db_type is 'mysql', but no valid MySQLConfig found.")
            values["config"]["MySQL"] = MySQLConfig(**config["MySQL"])
        else:
            raise ValueError("db_type must be either 'mongo' or 'mysql'.")

        return values


class KafkaBrokerConfig(BaseModel):
    bootstrap_servers: str
    security_protocol: str = Field(default="PLAINTEXT", enum=["PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"])
    schema_registry_url: str


class RabbitMQBrokerConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    virtual_host: str
    queue: str


class MessageBrokerConfig(BaseModel):
    mb_type: str = Field(..., enum=["kafka", "rabbitmq"])
    config: Dict[str, Any]

    @model_validator(mode='before')
    def validate_broker_config(cls, values):
        mb_type = values.get("mb_type")
        config = values.get("config")

        if mb_type == "kafka":
            if "KafkaBroker" not in config or not isinstance(config["KafkaBroker"], dict):
                raise ValueError("mb_type is 'kafka', but no valid KafkaBroker configuration found.")
            values["config"]["KafkaBroker"] = KafkaBrokerConfig(**config["KafkaBroker"])
        elif mb_type == "rabbitmq":
            if "RabbitMQBroker" not in config or not isinstance(config["RabbitMQBroker"], dict):
                raise ValueError("mb_type is 'rabbitmq', but no valid RabbitMQBroker configuration found.")
            values["config"]["RabbitMQBroker"] = RabbitMQBrokerConfig(**config["RabbitMQBroker"])
        else:
            raise ValueError("mb_type must be either 'kafka' or 'rabbitmq'.")

        return values


class Config(BaseModel):
    Settings: SettingsConfig
    Tasks: List[TaskConfig]
    DataBase: DataBaseConfig
    MessageBroker: MessageBrokerConfig


def to_snake_case(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


# Enhanced load_config function with dynamic name generation
def load_config(file_path: str) -> Config:
    with open(file_path, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)
        return Config(**config_data)

