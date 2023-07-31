from pydantic import BaseModel as _BaseModel

class BaseModel(_BaseModel):
    """ Extension of Pydantic's BaseModel to enable ORM extension """
    model_config = {"from_attributes": True}
