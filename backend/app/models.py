from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PriceData(BaseModel):
    type: str
    value: float


class OCRResponse(BaseModel):
    success: bool
    prices: List[PriceData]
    raw_text: str
    timestamp: str


class FuelPriceResponse(BaseModel):
    id: int
    latitude: Optional[float]
    longitude: Optional[float]
    benzin_95: Optional[float]
    benzin_98: Optional[float]
    diesel: Optional[float]
    created_at: datetime
