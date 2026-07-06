import os, json

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))

    search_urls = inp.get("search_urls")
    contacted_urls = inp.get("contacted_urls")

    if search_urls is None:
        raise ValueError("'search_urls' is required and must be a list of LinkedIn profile URL strings.")
    if contacted_urls is None:
        raise ValueError("'contacted_urls' is required and must be a list of LinkedIn profile URL strings.")
    if not isinstance(search_urls, list):
        raise ValueError("'search_urls' must be a list.")
    if not isinstance(contacted_urls, list):
        raise ValueError("'contacted_urls' must be a list.")

    cap = int(inp.get("cap", 25))
    cap = min(cap, 25)

    def normalize(url: str) -> str:
        url = url.strip().rstrip("/").lower()
        if url.startswith("http://"):
            url = "https://" + url[7:]
        if not url.startswith("https://"):
            url = "https://" + url
        return url

    normalized_contacted = set(normalize(u) for u in contacted_urls if isinstance(u, str) and u.strip())

    seen = set()
    net_new = []
    for url in search_urls:
        if not isinstance(url, str) or not url.strip():
            continue
        norm = normalize(url)
        if norm in normalized_contacted:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        net_new.append(norm)
        if len(net_new) >= cap:
            break

    result = {
        "net_new_profiles": net_new,
        "net_new_count": len(net_new),
        "search_total": len(search_urls),
        "contacted_total": len(contacted_urls),
        "cap_applied": cap
    }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))