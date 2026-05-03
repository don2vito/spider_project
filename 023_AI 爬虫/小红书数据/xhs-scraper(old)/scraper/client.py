"""
XhsClient wrapper with sign server integration.
Manages XhsClient instances and provides signing via Playwright sign server.
"""
import time
import logging
import requests as http_requests
from xhs import XhsClient

logger = logging.getLogger(__name__)

SIGN_SERVER_URL = "http://localhost:5005"
MAX_RETRIES = 3
RETRY_DELAY = 1

# Track sign server availability to avoid repeated failed calls
_sign_server_available = True


def _extract_a1(cookie_str: str) -> str:
    """Extract a1 value from cookie string."""
    for part in cookie_str.split(";"):
        kv = part.strip().split("=", 1)
        if len(kv) == 2 and kv[0].strip() == "a1":
            return kv[1].strip()
    return ""


def _sign(uri: str, data=None, a1="", web_session=""):
    """
    Call the sign server to get X-s and X-t signatures.
    Falls back to xhs built-in sign when sign server is unavailable.
    """
    global _sign_server_available

    # If sign server was recently unavailable, skip it and use built-in directly
    if _sign_server_available:
        for attempt in range(MAX_RETRIES):
            try:
                payload = data if data else ""
                if isinstance(payload, dict):
                    import json
                    payload = json.dumps(payload, separators=(",", ":"))

                resp = http_requests.post(
                    f"{SIGN_SERVER_URL}/sign",
                    json={"uri": uri, "data": payload, "a1": a1, "web_session": web_session},
                    timeout=10,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    x_s = result.get("X-s", "")
                    x_t = result.get("X-t", "")
                    if x_s:
                        return {"X-s": x_s, "X-t": x_t}
                    else:
                        logger.warning(f"Sign server returned empty X-s for {uri}")
                else:
                    logger.warning(f"Sign server returned {resp.status_code}")
            except http_requests.ConnectionError:
                logger.warning(f"Sign server not reachable (attempt {attempt + 1}/{MAX_RETRIES})")
            except Exception as e:
                logger.warning(f"Sign error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")

            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

        # Mark sign server as unavailable to avoid repeated failed calls
        _sign_server_available = False
        logger.warning("Sign server unavailable, switching to built-in sign")

    # Fallback: use xhs built-in sign function
    try:
        from xhs.help import sign as built_in_sign
        result = built_in_sign(uri, data, a1=a1)
        logger.info(f"Using built-in sign for {uri}")
        return {"X-s": result.get("x-s", ""), "X-t": result.get("x-t", "")}
    except Exception as e:
        logger.error(f"Built-in sign also failed: {e}")
        # Last resort: return timestamp only (will likely fail but won't crash)
        return {"X-s": "", "X-t": str(int(time.time() * 1000))}


class ClientManager:
    """Manages XhsClient instances, keyed by a1 cookie value."""

    _instances: dict = {}

    @classmethod
    def get_client(cls, cookie: str) -> XhsClient:
        """Get or create an XhsClient for the given cookie."""
        a1 = _extract_a1(cookie)

        if a1 and a1 in cls._instances:
            client = cls._instances[a1]
            client.cookie = cookie  # Update cookie
            return client

        # Create new client with external sign function
        client = XhsClient(
            cookie=cookie,
            sign=_sign,
            timeout=15,
        )

        if a1:
            cls._instances[a1] = client

        return client

    @classmethod
    def remove_client(cls, cookie: str):
        """Remove a client instance."""
        a1 = _extract_a1(cookie)
        if a1 and a1 in cls._instances:
            del cls._instances[a1]

    @classmethod
    def clear(cls):
        """Clear all client instances."""
        cls._instances.clear()


def check_sign_server() -> bool:
    """Check if the sign server is running and ready."""
    global _sign_server_available
    try:
        resp = http_requests.get(f"{SIGN_SERVER_URL}/status", timeout=3)
        if resp.status_code == 200:
            ready = resp.json().get("ready", False)
            if ready:
                _sign_server_available = True  # Reset flag when server is back
            return ready
    except Exception:
        _sign_server_available = False
    return False


def update_sign_server_cookie(cookie: str):
    """Update cookies in the sign server's browser context."""
    try:
        http_requests.post(
            f"{SIGN_SERVER_URL}/update_cookie",
            json={"cookie": cookie},
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Failed to update sign server cookie: {e}")
