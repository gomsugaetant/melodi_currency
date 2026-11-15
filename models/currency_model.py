from datetime import datetime
from core.orm.model import BaseModel, Mapped, mapped_column, String, DateTime
from sqlalchemy import Numeric, ForeignKey
from modules.melodi_currency.config import CurrencyTables as BaseTables

class CurrencyModel(BaseModel):
    __tablename__ = BaseTables.CURRENCIES

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)

class ExchangeRateModel(BaseModel):
    __tablename__ = BaseTables.EXCHANGE_RATES

    from_currency: Mapped[str] = mapped_column(
        String(3),
        ForeignKey(f"{BaseTables.CURRENCIES}.code", ondelete="CASCADE"),
        primary_key=True
    )
    to_currency: Mapped[str] = mapped_column(
        String(3),
        ForeignKey(f"{BaseTables.CURRENCIES}.code", ondelete="CASCADE"),
        primary_key=True
    )
    rate: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
