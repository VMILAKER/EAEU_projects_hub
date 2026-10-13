from pydantic import BaseModel, ConfigDict


class Upload(BaseModel):
    name: str
    description: str
    comments: str




    model_config = ConfigDict(str_max_length=10)