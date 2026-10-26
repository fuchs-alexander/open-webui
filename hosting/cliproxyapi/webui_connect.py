"""Verbindet Open WebUI mit dem CLIProxyAPI-Gateway. Laeuft im Container open-webui.
Erwartet PW (Admin-Passwort) und GW_KEY in der Umgebung; gibt beides nie aus."""
import json, os, sys, urllib.request, urllib.error

BASE = "http://127.0.0.1:8080"
GATEWAY = "http://cliproxyapi:8317/v1"

MODELS = [
    ("gpt-6.1-sol", "ChatGPT · GPT-6.1 Sol", "ChatGPT"),
    ("gpt-6-sol", "ChatGPT · GPT-6 Sol", "ChatGPT"),
    ("gpt-6-astra", "ChatGPT · GPT-6 Astra", "ChatGPT"),
    ("gpt-6-luna", "ChatGPT · GPT-6 Luna", "ChatGPT"),
    ("gpt-5.6-sol", "ChatGPT · GPT-5.6 Sol", "ChatGPT"),
    ("gpt-5.6-terra", "ChatGPT · GPT-5.6 Terra", "ChatGPT"),
    ("gpt-5.6-luna", "ChatGPT · GPT-5.6 Luna", "ChatGPT"),
    ("claude-opus-5-5", "Claude · Opus 5.5", "Claude"),
    ("claude-fable-5-1", "Claude · Fable 5.1", "Claude"),
    ("claude-sonnet-5-5", "Claude · Sonnet 5.5", "Claude"),
    ("claude-haiku-5-5", "Claude · Haiku 5.5", "Claude"),
]
DESCRIPTIONS = {
    "ChatGPT": "Gemeinsamer ChatGPT-Pro-Account ueber das Posylka-Gateway. Limits gelten fuer alle gemeinsam.",
    "Claude": "Gemeinsames Claude-Abo ueber das Posylka-Gateway. Limits gelten fuer alle gemeinsam.",
}


def call(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=None if body is None else json.dumps(body).encode())
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


status, auth = call("POST", "/api/v1/auths/signin",
                    body={"email": "nomobo@gmail.com", "password": os.environ["PW"]})
if status != 200:
    sys.exit(f"Admin-Login fehlgeschlagen: {status}")
token = auth["token"]

mode = sys.argv[1]
if mode == "backup":
    status, cfg = call("GET", "/openai/config", token)
    print(json.dumps(cfg))
elif mode == "apply":
    status, cfg = call("GET", "/openai/config", token)
    urls, keys, configs = cfg["OPENAI_API_BASE_URLS"], cfg["OPENAI_API_KEYS"], cfg["OPENAI_API_CONFIGS"]
    # Nur der unbenutzte Werkseintrag (api.openai.com ohne Schluessel) wird ersetzt.
    kept = [(u, k, configs.get(str(i), {})) for i, (u, k) in enumerate(zip(urls, keys))
            if u != GATEWAY and not (u == "https://api.openai.com/v1" and not k)]
    kept.append((GATEWAY, os.environ["GW_KEY"], {
        "enable": True, "connection_type": "external", "auth_type": "bearer",
        "prefix_id": "", "tags": [{"name": "Posylka-Gateway"}],
        "model_ids": [m[0] for m in MODELS],
    }))
    form = {
        "ENABLE_OPENAI_API": True,
        "OPENAI_API_BASE_URLS": [u for u, _, _ in kept],
        "OPENAI_API_KEYS": [k for _, k, _ in kept],
        "OPENAI_API_CONFIGS": {str(i): c for i, (_, _, c) in enumerate(kept)},
    }
    status, res = call("POST", "/openai/config/update", token, form)
    print("config update:", status, "urls:", res.get("OPENAI_API_BASE_URLS") if status == 200 else res)
    for model_id, name, provider in MODELS:
        body = {
            "id": model_id, "base_model_id": None, "name": name,
            "meta": {"description": DESCRIPTIONS[provider], "tags": [{"name": provider}],
                     "capabilities": {"vision": True, "file_upload": True, "citations": True}},
            "params": {},
            "access_grants": [{"principal_type": "user", "principal_id": "*", "permission": "read"}],
            "is_active": True,
        }
        status, res = call("POST", "/api/v1/models/create", token, body)
        if status != 200:
            status, res = call("POST", f"/api/v1/models/model/update?id={model_id}", token, body)
        print(f"model {model_id}: {status}")
elif mode == "restore":
    # Rueckweg: gesicherten Stand aus "backup" (JSON auf stdin) zurueckschreiben.
    # Die Modelleintraege bleiben; ohne Verbindung sieht sie niemand.
    saved = json.load(sys.stdin)
    status, res = call("POST", "/openai/config/update", token, {
        k: saved[k] for k in ("ENABLE_OPENAI_API", "OPENAI_API_BASE_URLS", "OPENAI_API_KEYS", "OPENAI_API_CONFIGS")})
    print("config restore:", status, "urls:", res.get("OPENAI_API_BASE_URLS") if status == 200 else res)
elif mode == "verify":
    status, cfg = call("GET", "/openai/config", token)
    print("enable:", cfg["ENABLE_OPENAI_API"], "urls:", cfg["OPENAI_API_BASE_URLS"],
          "keys set:", [bool(k) for k in cfg["OPENAI_API_KEYS"]])
    status, models = call("GET", "/api/models", token)
    print("admin sieht:", sorted(m["id"] for m in models.get("data", [])))
