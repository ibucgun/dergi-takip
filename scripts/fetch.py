#!/usr/bin/env python3
"""Dergilerde yeni çıkan (online-first / in press dahil) makaleleri bulur.

CrossRef'ten DOI kayıt tarihine göre yeni makaleleri çeker, daha önce
görülenleri (data/articles.json) eler, özeti eksik olanları PubMed ve
OpenAlex'ten tamamlar ve sonucu data/pending.json dosyasına yazar.
Sadece standart kütüphane kullanır.
"""
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MAILTO = "drismailbucgun@gmail.com"
UA = f"dergi-takip/1.0 (mailto:{MAILTO})"
FIRST_RUN_DAYS = 7
OVERLAP_DAYS = 3

SKIP_TITLE = re.compile(
    r"^\s*(corrigendum|erratum|correction|errors? in\b|incorrect|missing\b|"
    r"retraction|retracted|expression of concern|notice of|withdrawn|"
    r"editorial board|issue information|table of contents|cover\b)",
    re.I,
)


def get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  tekrar deneniyor ({e})", file=sys.stderr)
            time.sleep(3 * (attempt + 1))


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    text = re.sub(r"^\s*(abstract|summary)\s*", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def load_json(path, default):
    return json.loads(path.read_text("utf-8")) if path.exists() else default


def crossref(journal, since):
    filt = ",".join([f"issn:{i}" for i in journal["issn"]] + [f"from-created-date:{since}"])
    items, cursor = [], "*"
    while True:
        q = urllib.parse.urlencode({
            "filter": filt, "rows": 200, "cursor": cursor, "mailto": MAILTO,
            "select": "DOI,title,author,created,abstract,type",
        })
        msg = json.loads(get(f"https://api.crossref.org/works?{q}"))["message"]
        items += msg["items"]
        if len(msg["items"]) < 200:
            return items
        cursor = msg["next-cursor"]


def authors(item):
    names = []
    for a in item.get("author", []):
        n = " ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name", "")
        if n:
            names.append(n)
    if len(names) > 3:
        return ", ".join(names[:3]) + " ve ark."
    return ", ".join(names)


def pubmed_abstracts(dois):
    """DOI -> (özet, pmid)"""
    found = {}
    for i in range(0, len(dois), 40):
        chunk = dois[i:i + 40]
        term = " OR ".join(f'"{d}"[doi]' for d in chunk)
        q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": 200, "retmode": "json"})
        ids = json.loads(get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{q}"))["esearchresult"]["idlist"]
        time.sleep(0.4)
        if not ids:
            continue
        q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "xml"})
        root = ET.fromstring(get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{q}"))
        time.sleep(0.4)
        for art in root.iter("PubmedArticle"):
            doi = next((x.text for x in art.iter("ArticleId") if x.get("IdType") == "doi" and x.text), None)
            parts = []
            for a in art.iter("AbstractText"):
                txt = "".join(a.itertext()).strip()
                label = a.get("Label")
                parts.append(f"{label}: {txt}" if label else txt)
            pmid = art.findtext(".//PMID")
            if doi:
                found[doi.lower()] = (" ".join(parts).strip(), pmid)
    return found


def openalex_abstracts(dois):
    found = {}
    for i in range(0, len(dois), 40):
        chunk = dois[i:i + 40]
        q = urllib.parse.urlencode({
            "filter": "doi:" + "|".join(chunk), "per-page": 50,
            "select": "doi,abstract_inverted_index", "mailto": MAILTO,
        })
        for w in json.loads(get(f"https://api.openalex.org/works?{q}")).get("results", []):
            inv = w.get("abstract_inverted_index")
            if not inv or not w.get("doi"):
                continue
            words = sorted((p, word) for word, ps in inv.items() for p in ps)
            found[w["doi"].replace("https://doi.org/", "").lower()] = " ".join(x for _, x in words)
    return found


def main():
    journals = load_json(ROOT / "journals.json", [])
    articles = load_json(DATA / "articles.json", [])
    state = load_json(DATA / "state.json", {})
    seen = {a["doi"].lower() for a in articles}
    today = dt.date.today()

    new = []
    for j in journals:
        last = state.get("last_run", {}).get(j["id"])
        if last:
            since = dt.date.fromisoformat(last) - dt.timedelta(days=OVERLAP_DAYS)
        else:
            since = today - dt.timedelta(days=FIRST_RUN_DAYS)
        try:
            items = crossref(j, since.isoformat())
        except Exception as e:
            print(f"HATA {j['name']}: {e}", file=sys.stderr)
            continue
        count = 0
        for it in items:
            doi = it["DOI"].lower()
            title = clean((it.get("title") or [""])[0])
            if doi in seen or not title or SKIP_TITLE.match(title):
                continue
            if it.get("type") not in ("journal-article", None):
                continue
            seen.add(doi)
            parts = it["created"]["date-parts"][0]
            new.append({
                "doi": doi,
                "journal": j["id"],
                "title": title,
                "authors": authors(it),
                "online": "-".join(f"{p:02d}" for p in parts),
                "abstract": clean(it.get("abstract")),
            })
            count += 1
        state.setdefault("last_run", {})[j["id"]] = today.isoformat()
        print(f"{j['name']}: {count} yeni")
        time.sleep(1)

    missing = [a["doi"] for a in new if len(a["abstract"]) < 100]
    if missing:
        try:
            pm = pubmed_abstracts(missing)
            for a in new:
                if a["doi"] in pm:
                    ab, pmid = pm[a["doi"]]
                    a["pmid"] = pmid
                    if len(a["abstract"]) < 100 and ab:
                        a["abstract"] = ab
        except Exception as e:
            print(f"PubMed hatası: {e}", file=sys.stderr)
    missing = [a["doi"] for a in new if len(a["abstract"]) < 100]
    if missing:
        try:
            oa = openalex_abstracts(missing)
            for a in new:
                if len(a["abstract"]) < 100 and oa.get(a["doi"]):
                    a["abstract"] = oa[a["doi"]]
        except Exception as e:
            print(f"OpenAlex hatası: {e}", file=sys.stderr)

    # Önceki çalışmadan kalıp özetlenmemiş olanlar da korunur
    pending = load_json(DATA / "pending.json", [])
    pending_dois = {p["doi"] for p in pending}
    pending += [a for a in new if a["doi"] not in pending_dois]
    (DATA / "pending.json").write_text(json.dumps(pending, ensure_ascii=False, indent=1), "utf-8")
    (DATA / "state.json").write_text(json.dumps(state, indent=1), "utf-8")
    with_ab = sum(1 for a in new if a["abstract"])
    print(f"Toplam {len(new)} yeni makale ({with_ab} tanesinin özeti var). Özet bekleyen: {len(pending)}")


if __name__ == "__main__":
    main()
