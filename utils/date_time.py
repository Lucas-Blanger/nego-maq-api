from datetime import datetime, timezone, timedelta

BRASIL_TZ = timezone(timedelta(hours=-3))


def agora_brasil():
    return datetime.now(BRASIL_TZ)


def utc_para_brasil(dt_utc):
    if dt_utc is None:
        return None

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    return dt_utc.astimezone(BRASIL_TZ)


def brasil_para_utc(dt_brasil):
    if dt_brasil is None:
        return None

    if dt_brasil.tzinfo is None:
        dt_brasil = dt_brasil.replace(tzinfo=BRASIL_TZ)

    return dt_brasil.astimezone(timezone.utc)


def formatar_brasil(dt, formato="%d/%m/%Y %H:%M:%S"):

    if dt is None:
        return None

    if dt.tzinfo is None or dt.tzinfo != BRASIL_TZ:
        dt = utc_para_brasil(dt)

    return dt.strftime(formato)
