from pydantic import BaseModel


class FavoriteRequest(BaseModel):
    dish_name: str
    category_id: str = ""
    category_name: str = ""
    image: str = ""


class DietRecordRequest(BaseModel):
    dish_name: str
    category_id: str = ""
    category_name: str = ""
    image: str = ""
