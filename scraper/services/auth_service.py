import json
import os
import time
import requests


AUTH = None
AUTH_MTIME = None
SESSION = requests.Session()


def obtener_auth():

    global AUTH, AUTH_MTIME

    try:
        mtime = os.path.getmtime(
            "auth.json"
        )
    except FileNotFoundError:
        mtime = None

    if AUTH is not None and AUTH_MTIME == mtime:

        return AUTH

    with open(
        "auth.json",
        "r",
        encoding="utf-8"
    ) as f:

        AUTH = json.load(f)
        AUTH_MTIME = mtime

    return AUTH


def invalidar_auth_cache():

    global AUTH, AUTH_MTIME

    AUTH = None
    AUTH_MTIME = None


def guardar_auth(auth):

    global AUTH, AUTH_MTIME

    with open(
        "auth.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            auth,
            f,
            indent=4,
            ensure_ascii=False
        )

    AUTH = auth
    try:
        AUTH_MTIME = os.path.getmtime(
            "auth.json"
        )
    except FileNotFoundError:
        AUTH_MTIME = None


def obtener_token():

    auth = obtener_auth()

    if isinstance(auth, str):
        return auth

    if isinstance(auth, dict):
        return auth.get("token") or auth.get("Token")

    return None


def obtener_cookies():

    auth = obtener_auth()

    if isinstance(auth, dict):
        return auth.get("cookies") or auth.get("Cookies")

    return None


def obtener_headers():

    token = obtener_token()

    if not token:
        raise ValueError(
            "auth.json no tiene token válido."
        )

    headers = {

        "Authorization":
        f"Bearer {token}",

        "Content-Type":
        "application/json",

        "Accept":
        "application/json, text/plain, */*",

        "Origin":
        "https://tribunalelectronico.pjedomex.gob.mx",

        "Referer":
        "https://tribunalelectronico.pjedomex.gob.mx/",

        "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/136.0.0.0 "
            "Safari/537.36"
        )
    }

    cookies = obtener_cookies()
    if cookies:
        headers["Cookie"] = cookies

    return headers


def _obtener_expires_at(auth):

    if not isinstance(auth, dict):
        return None

    expires_at = auth.get("expires_at")
    if expires_at is None:
        return None

    try:
        return float(expires_at)
    except (TypeError, ValueError):
        return None


def _obtener_login_payload():
    return {
        "cveTipoDispositivo": "1",
        "ipPublica": "201.150.33.188",
        "ipUsuario": None,
        "latitud": None,
        "longitud": None,
        "password": "$2a$08$RK/TT8zxX9mFc3dpBOFnAeG2Yk8OZs/VoE8l6WrXt/bTc1U/kB5g2",
        "user": "8082922"
    }


def login_automatico():

    payload = _obtener_login_payload()
    if not payload:
        return False

    url = (
        "https://tribunalelectronicobk.pjedomex.gob.mx"
        "/api/auth/login"
    )

    response = SESSION.post(
        url,
        json=payload,
        timeout=60
    )
    response.raise_for_status()

    body = response.json()
    data = body.get("data") if isinstance(body, dict) else None

    if not isinstance(data, dict):
        return False

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expires_in = data.get("expires_in")

    if not access_token:
        return False

    now = time.time()
    expires_at = None
    try:
        if expires_in is not None:
            expires_at = now + int(expires_in)
    except (TypeError, ValueError):
        expires_at = None

    auth_actual = {}
    try:
        auth_actual = obtener_auth()
        if not isinstance(auth_actual, dict):
            auth_actual = {}
    except Exception:
        auth_actual = {}

    auth_actual.update(
        {
            "token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "expires_at": expires_at,
            "obtained_at": now
        }
    )

    guardar_auth(auth_actual)
    return True


def asegurar_token_fresco(
    margen_segundos=60
):

    try:
        auth = obtener_auth()
    except Exception:
        auth = None

    expires_at = _obtener_expires_at(
        auth
    )

    if expires_at is None:
        return False

    if time.time() < (expires_at - margen_segundos):
        return True

    return login_automatico()


def request_get(
    url,
    params=None,
    timeout=120,
    stream=False,
    max_reintentos=3
):

    last_error = None

    for intento in range(max_reintentos):

        asegurar_token_fresco()

        headers = obtener_headers()

        response = SESSION.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
            stream=stream
        )

        if response.status_code == 401:
            invalidar_auth_cache()
            login_automatico()
            last_error = requests.exceptions.HTTPError(
                "401 Unauthorized",
                response=response
            )
            time.sleep(1 + (intento * 2))
            continue

        response.raise_for_status()
        return response

    if last_error:
        raise last_error

    raise RuntimeError(
        "request_get falló sin respuesta."
    )
