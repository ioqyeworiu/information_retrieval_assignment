from fastapi import Query
from  pydantic import BaseModel


class Query(BaseModel):
    query_n: int = Query(default=21)
    similarity_type: str = Query(default="embedding")