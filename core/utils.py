import re
from datetime import datetime

ISBN_RE = re.compile(r'^[0-9\-]{5,20}$')

def validar_isbn(isbn: str) -> bool:
    isbn = isbn.strip()
    if not isbn:
        return False
    return bool(ISBN_RE.match(isbn))

def validar_fecha_iso(fecha: str) -> bool:
    """Valida si una cadena es una fecha en formato ISO (YYYY-MM-DD) y que sea una fecha real."""
    try:
        datetime.fromisoformat(fecha)
        return True
    except Exception:
        return False