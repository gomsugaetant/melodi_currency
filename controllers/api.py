from __future__ import annotations

from typing import Any
from core.routing import Request, Response
from sqlalchemy import select, delete
from modules.melodi_currency.models.currency_model import CurrencyModel, ExchangeRateModel


class CurrencyAPIController:
    @staticmethod
    async def list_currencies(request: Request, response: Response):
        async with request.module.app.db.get_session() as session:
            stmt = select(CurrencyModel).order_by(CurrencyModel.name)
            res = await session.execute(stmt)
            currencies = [
                {"code": c.code, "name": c.name, "symbol": c.symbol}
                for c in res.scalars().all()
            ]
            return response.send_json({"success": True, "data": currencies})

    @staticmethod
    async def save_currency(request: Request, response: Response):
        data = await request.json()
        code = (data.get("code") or "").strip().upper()
        name = (data.get("name") or "").strip()
        symbol = (data.get("symbol") or "").strip()

        if not code or not name or not symbol:
            return response.send_json({"success": False, "error": "Champs code, nom et symbole requis"}, status=400)

        async with request.module.app.db.get_session() as session:
            stmt = select(CurrencyModel).filter_by(code=code)
            res = await session.execute(stmt)
            curr = res.scalar_one_or_none()
            if not curr:
                curr = CurrencyModel(code=code, name=name, symbol=symbol)
                session.add(curr)
            else:
                curr.name = name
                curr.symbol = symbol
            await session.commit()

        return response.send_json({"success": True, "data": {"code": code, "name": name, "symbol": symbol}})

    @staticmethod
    async def delete_currency(request: Request, response: Response):
        code = (request.args.get("code") or (await request.json()).get("code") or "").strip().upper()
        if not code:
            return response.send_json({"success": False, "error": "Code devise requis"}, status=400)

        async with request.module.app.db.get_session() as session:
            stmt = delete(CurrencyModel).where(CurrencyModel.code == code)
            await session.execute(stmt)
            await session.commit()

        return response.send_json({"success": True, "message": f"Devise {code} supprimée"})

    @staticmethod
    async def list_exchange_rates(request: Request, response: Response):
        async with request.module.app.db.get_session() as session:
            stmt = select(ExchangeRateModel).order_by(ExchangeRateModel.from_currency)
            res = await session.execute(stmt)
            rates = [
                {
                    "from_currency": r.from_currency,
                    "to_currency": r.to_currency,
                    "rate": float(r.rate),
                    "updated_at": r.updated_at.isoformat() if r.updated_at else None
                }
                for r in res.scalars().all()
            ]
            return response.send_json({"success": True, "data": rates})

    @staticmethod
    async def save_exchange_rate(request: Request, response: Response):
        data = await request.json()
        from_curr = (data.get("from_currency") or "").strip().upper()
        to_curr = (data.get("to_currency") or "").strip().upper()
        rate_val = float(data.get("rate") or 0.0)

        if not from_curr or not to_curr or rate_val <= 0:
            return response.send_json({"success": False, "error": "Devises et taux valide requis"}, status=400)

        async with request.module.app.db.get_session() as session:
            stmt = select(ExchangeRateModel).filter_by(from_currency=from_curr, to_currency=to_curr)
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                existing = ExchangeRateModel(from_currency=from_curr, to_currency=to_curr, rate=rate_val)
                session.add(existing)
            else:
                existing.rate = rate_val
            await session.commit()

        return response.send_json({"success": True, "data": {"from_currency": from_curr, "to_currency": to_curr, "rate": rate_val}})
