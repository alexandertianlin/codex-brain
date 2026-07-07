from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


PROVIDERS = [
    {
        "name": "allrealai",
        "base_url": "https://ai.allrealai.com/v1",
        "models_url": "https://ai.allrealai.com/v1/models",
        "key_env": "ALLREALAI_API_KEY",
        "fallback_key_env": "OPENAI_API_KEY",
    },
    {
        "name": "openai",
        "base_url": "https://api.openai.com/v1",
        "models_url": "https://api.openai.com/v1/models",
        "key_env": "OPENAI_API_KEY",
    },
]


def check_provider(name: str = "allrealai", timeout: float = 8.0) -> dict:
    provider = next((item for item in PROVIDERS if item["name"] == name), PROVIDERS[0])
    api_key = os.environ.get(provider["key_env"], "")
    if not api_key and provider.get("fallback_key_env"):
        api_key = os.environ.get(provider["fallback_key_env"], "")
    if not api_key:
        detail = f"{provider['key_env']} is not set"
        if provider.get("fallback_key_env"):
            detail += f" and {provider['fallback_key_env']} fallback is not set"
        return {"name": provider["name"], "status": "missing-key", "detail": detail}
    req = urllib.request.Request(provider["models_url"], headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(512).decode("utf-8", errors="replace")
        return {"name": provider["name"], "status": "ok", "http_status": response.status, "sample": body[:160]}
    except urllib.error.HTTPError as exc:
        detail = exc.read(512).decode("utf-8", errors="replace")
        return {"name": provider["name"], "status": "http-error", "http_status": exc.code, "detail": detail[:300]}
    except Exception as exc:
        return {"name": provider["name"], "status": "error", "detail": str(exc)}


def main() -> int:
    print(json.dumps(check_provider(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
