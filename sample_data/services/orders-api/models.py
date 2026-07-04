"""Data models for orders-api (SYNTHETIC / fictional)."""

from enum import StrEnum

from pydantic import BaseModel, Field


class OrderStatus(StrEnum):
    RESERVED = "reserved"
    FULFILLING = "fulfilling"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class LineItem(BaseModel):
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
    quantity: int = Field(gt=0, le=999)


class Order(BaseModel):
    customer_id: str
    line_items: list[LineItem]
