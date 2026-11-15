from __future__ import annotations

from core.db.base_module_tables import BaseModuleTables

MODULE_NAME = "melodi_currency"
PREFIX_TABLE = "ml_base_"


class CurrencyTables(BaseModuleTables):
    CURRENCIES = f"{PREFIX_TABLE}currencies"
    EXCHANGE_RATES = f"{PREFIX_TABLE}exchange_rates"
