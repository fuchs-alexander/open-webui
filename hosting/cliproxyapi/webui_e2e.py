"""End-to-End-Tests ueber Open WebUI -> CLIProxyAPI. Laeuft im Container open-webui."""
import json, os, sys, time, threading, urllib.request, urllib.error

BASE = "http://127.0.0.1:8080"


def call(path, body=None, token=None, stream=False, timeout=180):
    req = urllib.request.Request(BASE + path, data=None if body is None else json.dumps(body).encode())
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            return r.status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


def text_of(raw):
    if raw.lstrip().startswith("{"):
        j = json.loads(raw)
        return j["choices"][0]["message"].get("content") or ""
    out = []
    for line in raw.splitlines():
        if line.startswith("data: {"):
            j = json.loads(line[6:])
            for c in j.get("choices", []):
                out.append((c.get("delta") or {}).get("content") or "")
    return "".join(out)


status, auth = call("/api/v1/auths/signin", {"email": "nomobo@gmail.com", "password": os.environ["PW"]})
token = json.loads(auth)["token"]
models = sys.argv[1:] or ["gpt-6-sol", "claude-sonnet-5-5"]

for m in models:
    print(f"--- {m}")
    # 1. Streaming
    t = time.time()
    s, raw = call("/api/chat/completions", {"model": m, "stream": True,
                  "messages": [{"role": "user", "content": "Antworte nur mit: Streaming ok"}]}, token)
    print("stream:", s, repr(text_of(raw)[:60]), f"{time.time()-t:.1f}s")

    # 2. Lange Historie (60 Nachrichten, Fakt ganz am Anfang)
    hist = [{"role": "system", "content": "Du bist ein knapper Assistent."},
            {"role": "user", "content": "Merke dir: Der Projektcode lautet KIWI-7319."},
            {"role": "assistant", "content": "Notiert."}]
    for i in range(29):
        hist += [{"role": "user", "content": f"Fuelltext {i}: " + "Lorem ipsum dolor sit amet. " * 20},
                 {"role": "assistant", "content": "Ok."}]
    hist.append({"role": "user", "content": "Wie lautet der Projektcode? Nur den Code."})
    s, raw = call("/api/chat/completions", {"model": m, "stream": True, "messages": hist}, token)
    print("lange Historie:", s, repr(text_of(raw)[:40]))

    # 3. Zwei parallele Sitzungen ohne Kontextvermischung
    res = {}
    def worker(word):
        msgs = [{"role": "user", "content": f"Das Geheimwort dieser Sitzung ist {word}."},
                {"role": "assistant", "content": "Verstanden."},
                {"role": "user", "content": "Nenne nur das Geheimwort dieser Sitzung."}]
        res[word] = text_of(call("/api/chat/completions", {"model": m, "stream": True, "messages": msgs}, token)[1])
    ts = [threading.Thread(target=worker, args=(w,)) for w in ("ZEDER", "MOEWE")]
    [x.start() for x in ts]; [x.join() for x in ts]
    print("parallel:", {k: v.strip()[:20] for k, v in res.items()},
          "ok" if all(k.lower() in v.lower() and (set(res) - {k}).pop().lower() not in v.lower() for k, v in res.items()) else "FEHLER")

    # 4. Funktions-Tool-Zyklus inklusive zweitem Modellturn (OpenAI-Format durch WebUI-Proxy)
    tools = [{"type": "function", "function": {"name": "lagerbestand", "description": "Liefert den Lagerbestand eines Artikels",
              "parameters": {"type": "object", "properties": {"artikel": {"type": "string"}}, "required": ["artikel"]}}}]
    msgs = [{"role": "user", "content": "Wie hoch ist der Lagerbestand von Artikel A-42? Nutze das Werkzeug."}]
    s, raw = call("/openai/chat/completions", {"model": m, "stream": False, "messages": msgs, "tools": tools}, token)
    try:
        msg = json.loads(raw)["choices"][0]["message"]
        tc = msg["tool_calls"][0]
        print("tool call:", s, tc["function"]["name"], tc["function"]["arguments"])
        msgs += [msg, {"role": "tool", "tool_call_id": tc["id"], "content": json.dumps({"artikel": "A-42", "bestand": 137})}]
        s, raw = call("/openai/chat/completions", {"model": m, "stream": False, "messages": msgs, "tools": tools}, token)
        print("zweiter Turn:", s, repr(text_of(raw)[:80]))
    except Exception as e:
        print("tool FEHLER:", s, raw[:300], e)

    # 5. Titelgenerierung (Hintergrundaufgabe)
    s, raw = call("/api/v1/tasks/title/completions", {"model": m, "messages": [
        {"role": "user", "content": "Wie plane ich eine Paketzustellung nach Polen?"},
        {"role": "assistant", "content": "Mit Posylka geht das so ..."}]}, token)
    try:
        print("titel:", s, repr(text_of(raw)[:80]))
    except Exception:
        print("titel:", s, raw[:200])
