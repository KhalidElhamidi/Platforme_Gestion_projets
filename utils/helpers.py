"""
Fonctions utilitaires.
"""

from datetime import datetime, date
from typing import Optional


def format_date(d: Optional[date], format_str: str = "%d/%m/%Y") -> str:
    """Formate une date pour l'affichage."""
    if d is None:
        return "Non défini"
    if isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d").date()
    return d.strftime(format_str)


def format_datetime(dt: Optional[datetime], format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Formate une datetime pour l'affichage."""
    if dt is None:
        return "Non défini"
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime(format_str)


def days_between(start: date, end: date) -> int:
    """Calcule le nombre de jours entre deux dates."""
    if isinstance(start, str):
        start = datetime.strptime(start, "%Y-%m-%d").date()
    if isinstance(end, str):
        end = datetime.strptime(end, "%Y-%m-%d").date()
    return (end - start).days


def is_overdue(deadline: date) -> bool:
    """Vérifie si une deadline est dépassée."""
    if deadline is None:
        return False
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    return deadline < date.today()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Tronque un texte s'il dépasse une certaine longueur."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formate un pourcentage."""
    return f"{value:.{decimals}f}%"


def get_status_emoji(status: str) -> str:
    """Retourne l'emoji correspondant à un statut."""
    emojis = {
        'TODO': '⬜',
        'IN_PROGRESS': '🔵',
        'REVIEW': '🟣',
        'COMPLETED': '✅',
        'BLOCKED': '🔴',
        'NOT_STARTED': '⬜',
        'ON_HOLD': '⏸️',
        'CANCELLED': '❌'
    }
    return emojis.get(status, '❓')


def get_priority_emoji(priority: str) -> str:
    """Retourne l'emoji correspondant à une priorité."""
    emojis = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🟠',
        'CRITICAL': '🔴'
    }
    return emojis.get(priority, '⚪')
