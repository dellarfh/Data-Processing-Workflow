from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderContract(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    order_id: str = Field(min_length=1)
    customer_id: int = Field(gt=0)
    amount: float = Field(ge=0)
    status: Literal["PAID", "PENDING", "CANCELLED"]
    transaction_date: datetime
    payment_date: datetime | None = None

    @model_validator(mode="after")
    def paid_requires_payment_date(self):
        if self.status == "PAID" and self.payment_date is None:
            raise ValueError(
                "payment_date wajib diisi jika status=PAID"
            )
        return self