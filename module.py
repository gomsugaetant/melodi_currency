from __future__ import annotations

from typing import Any
from core.module import ApplicationModule
from sqlalchemy import select
from modules.melodi_currency.controllers.api import CurrencyAPIController
from modules.melodi_currency.models.currency_model import CurrencyModel, ExchangeRateModel


class CurrencyModule(ApplicationModule):
    def __init__(self):
        super().__init__(name="melodi_currency", router_name="melodi_currency")

    async def load(self):
        # 1. Routes API
        self.api_router.add_route("/currencies", CurrencyAPIController.list_currencies, methods=["GET"])
        self.api_router.add_route("/rates", CurrencyAPIController.list_exchange_rates, methods=["GET"])

        self.api_admin_router.add_route("/currencies", CurrencyAPIController.list_currencies, methods=["GET"])
        self.api_admin_router.add_route("/currencies", CurrencyAPIController.save_currency, methods=["POST"])
        self.api_admin_router.add_route("/currencies/delete", CurrencyAPIController.delete_currency, methods=["POST"])
        self.api_admin_router.add_route("/rates", CurrencyAPIController.list_exchange_rates, methods=["GET"])
        self.api_admin_router.add_route("/rates", CurrencyAPIController.save_exchange_rate, methods=["POST"])

        # 2. Actions Hooks pour communication inter-modules
        self.add_action("get_currencies_and_rates", self.action_get_currencies_and_rates)
        self.add_action("convert_amount", self.action_convert_amount)

    async def action_get_currencies_and_rates(self, payload: dict | None = None) -> dict[str, Any]:
        async with self.app.db.get_session() as session:
            stmt_curr = select(CurrencyModel)
            res_curr = await session.execute(stmt_curr)
            currencies = [
                {"code": c.code, "name": c.name, "symbol": c.symbol}
                for c in res_curr.scalars().all()
            ]

            stmt_rates = select(ExchangeRateModel)
            res_rates = await session.execute(stmt_rates)
            rates = [
                {"from_currency": r.from_currency, "to_currency": r.to_currency, "rate": float(r.rate)}
                for r in res_rates.scalars().all()
            ]

            return {"currencies": currencies, "rates": rates}

    async def action_convert_amount(self, payload: dict) -> dict[str, Any]:
        amount = float(payload.get("amount", 0.0))
        from_curr = payload.get("from_currency")
        to_curr = payload.get("to_currency")

        if from_curr == to_curr:
            return {"amount": amount, "rate": 1.0, "converted_amount": amount}

        async with self.app.db.get_session() as session:
            stmt = select(ExchangeRateModel).filter_by(from_currency=from_curr, to_currency=to_curr)
            res = await session.execute(stmt)
            rate_obj = res.scalar_one_or_none()
            rate = float(rate_obj.rate) if rate_obj else 1.0
            return {
                "amount": amount,
                "rate": rate,
                "converted_amount": round(amount * rate, 4)
            }


module = CurrencyModule()
