"""Bot suhbatlarining holatlari (FSM — Finite State Machine)."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    """Ro'yxatdan o'tish anketasi qadamlari."""

    choosing_language = State()
    entering_name = State()
    entering_phone = State()
    choosing_factory = State()
    entering_custom_factory = State()
    entering_spot = State()


class ChangeLanguage(StatesGroup):
    """Profildan tilni o'zgartirish."""

    choosing = State()
