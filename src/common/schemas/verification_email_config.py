import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from ..exceptions.missing_config_exception import MissingConfigException

load_dotenv()


class VerificationConfig(BaseModel):
    domain_url: str = Field(..., description="URL of the application domain")
    sender_email: str = Field(..., description="Sender email address")
    sender_password: str = Field(..., description="Password or App Password for the sender email")
    smtp_host: str = Field(..., description="SMTP server hostname")
    smtp_port: int = Field(..., description="SMTP server port")

    def __init__(self, **kwargs):
        for field_name in self.__fields__:
            if field_name not in kwargs:
                env_value = os.getenv(f'VERIFICATION_{field_name.upper()}')
                if env_value is not None:
                    kwargs[field_name] = env_value

        super().__init__(**kwargs)

        for field_name, field_value in self.__dict__.items():
            if field_value is None:
                raise MissingConfigException(field_name)
