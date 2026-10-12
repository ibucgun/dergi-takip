#!/usr/bin/env python3
"""data/pending.json + data/summaries.json -> data/articles.json -> docs/index.html"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KEEP_DAYS = 90


def load_json(path, default):
    return json.loads(path.read_text("utf-8")) if path.exists() else default


def numbers(text):
    """Özetteki 3+ haneli sayılar (1.322 / 1322 / 1,322 aynı sayılır)."""
    return {re.sub(r"[.,\s]", "", n) for n in re.findall(r"\d[\d.,]*\d", text or "") if len(re.sub(r"[.,\s]", "", n)) >= 3}


def mismatched(pending):
    """Türkçe özetteki sayılar kendi abstract'ında değil de başka bir makalede geçiyorsa özet yanlış makaleye yazılmıştır."""
    bad = []
    for p in pending:
        nums = numbers(p.get("ozet", ""))
        if len(nums) < 2 or not p.get("abstract"):
            continue
        own = numbers(p["abstract"])
        if len(nums & own) / len(nums) >= 0.5:
            continue
        other = next((q for q in pending if q is not p and len(nums & numbers(q.get("abstract", ""))) / len(nums) >= 0.5), None)
        if other:
            bad.append((p, other))
    return bad


def main():
    journals = load_json(ROOT / "journals.json", [])
    articles = load_json(DATA / "articles.json", [])
    pending = load_json(DATA / "pending.json", [])
    summaries = {k.lower(): v for k, v in load_json(DATA / "summaries.json", {}).items()}
    # Özet tercihen pending.json'da makalenin kendi "ozet" alanına yazılır (yanlış eşleşmeyi önler)
    for p in pending:
        if p.get("ozet"):
            summaries[p["doi"]] = p["ozet"]
        elif summaries.get(p["doi"]):
            p["ozet"] = summaries[p["doi"]]
    bad = mismatched(pending)
    if bad:
        for p, q in bad:
            print(f"HATA: '{p['title'][:70]}' makalesinin özeti büyük olasılıkla '{q['title'][:70]}' makalesine ait.", file=sys.stderr)
        print("Özetleri düzeltip build.py'yi yeniden çalıştırın. Sayfa güncellenmedi.", file=sys.stderr)
        sys.exit(1)
    missing = [p["title"][:70] for p in pending if not summaries.get(p["doi"])]
    if missing:
        print(f"UYARI: {len(missing)} makalenin Türkçe özeti yok: " + "; ".join(missing[:5]), file=sys.stderr)
    today = dt.date.today().isoformat()

    known = {a["doi"]: a for a in articles}
    for p in pending:
        if p["doi"] in known:
            # Özeti sonradan bulunan makale: yeni Türkçe özet eskisinin yerine geçer
            a = known[p["doi"]]
            if summaries.get(p["doi"]):
                a["ozet"] = summaries[p["doi"]]
            if p.get("pmid"):
                a["pmid"] = p["pmid"]
            continue
        a = {k: v for k, v in p.items() if k not in ("abstract", "update")}
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
        "groups": load_json(ROOT / "groups.json", []),
        "journals": [{"id": j["id"], "name": j["name"], "url": j["url"], "group": j.get("group", "")} for j in journals],
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
