#!/usr/bin/env python3
"""data/pending.json + data/summaries.json -> data/articles.json -> docs/index.html"""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KEEP_DAYS = 90


def load_json(path, default):
    return json.loads(path.read_text("utf-8")) if path.exists() else default


def main():
    journals = load_json(ROOT / "journals.json", [])
    articles = load_json(DATA / "articles.json", [])
    pending = load_json(DATA / "pending.json", [])
    summaries = {k.lower(): v for k, v in load_json(DATA / "summaries.json", {}).items()}
    today = dt.date.today().isoformat()

    known = {a["doi"] for a in articles}
    for p in pending:
        if p["doi"] in known:
            continue
        a = {k: v for k, v in p.items() if k != "abstract"}
        a["ozet"] = summaries.get(p["doi"], "")
        a["added"] = today
        articles.append(a)
    # Sonradan yazılan özetler eski kayıtlara da işlenir
    for a in articles:
        if not a.get("ozet") and summaries.get(a["doi"]):
            a["ozet"] = summaries[a["doi"]]

    cutoff = (dt.date.today() - dt.timedelta(days=KEEP_DAYS)).isoformat()
    articles = [a for a in articles if a["added"] >= cutoff]
    articles.sort(key=lambda a: (a["added"], a["online"]), reverse=True)

    (DATA / "articles.json").write_text(json.dumps(articles, ensure_ascii=False, indent=1), "utf-8")
    (DATA / "pending.json").write_text("[]", "utf-8")
    (DATA / "summaries.json").write_text("{}", "utf-8")

    payload = {
        "updated": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "journals": [{"id": j["id"], "name": j["name"], "url": j["url"]} for j in journals],
        "articles": articles,
    }
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    template = (ROOT / "scripts" / "template.html").read_text("utf-8")
    page = template.replace("__DATA__", blob)
    # Pages kök klasörden veya /docs'tan yayınlanabilir; ikisine de yazılır
    for out in (ROOT, ROOT / "docs"):
        (out / "index.html").write_text(page, "utf-8")
        (out / ".nojekyll").write_text("", "utf-8")
    print(f"Sayfa üretildi: {len(articles)} makale")


if __name__ == "__main__":
    main()
