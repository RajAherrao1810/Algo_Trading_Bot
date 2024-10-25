from pydantic import BaseModel

class SymbolRequest(BaseModel):
    symbol: str

class TokenRequest(BaseModel):
    token: str

class IndexInfoResponse(BaseModel):
    index: str
