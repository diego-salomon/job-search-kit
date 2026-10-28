#!/usr/bin/env python3
"""
scan_portals.py -- scan company career portals (ATS APIs) for matching roles.

The free job boards (find-remote-jobs) skew US-locked and junior. Company career
portals are where the good roles actually live. This hits the public JSON APIs of
the major ATS platforms directly -- no key, no scraping, no browser.

  python3 scan_portals.py                          # scan portals.yml, write CSV
  python3 scan_portals.py --probe canonical,elastic # find which ATS a company uses
  python3 scan_portals.py --no-filter              # keep every role (audit mode)

Providers: greenhouse, ashby, lever, workable, recruitee, smartrecruiters.
"""
import argparse, csv, json, re, sys, urllib.request, urllib.error, ssl
from concurrent.futures import ThreadPoolExecutor

import yaml

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) portal-scan/1.0'}
CTX = ssl.create_default_context()


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


def norm(company, title, url, location, desc='', posted=''):
    return {'company': company, 'title': (title or '').strip(),
            'url': url or '', 'location': (location or '').strip(),
            'posted': (posted or '')[:10],
            'desc': re.sub(r'<[^>]+>', ' ', desc or '')[:20000]}


# ---- providers -------------------------------------------------------------

def p_greenhouse(name, slug):
    d = get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true')
    return [norm(name, j.get('title'), j.get('absolute_url'),
                 (j.get('location') or {}).get('name'), j.get('content', ''),
                 j.get('updated_at') or j.get('first_published', ''))
            for j in d.get('jobs', [])]


def p_greenhouse_eu(name, slug):
    d = get(f'https://boards-api.eu.greenhouse.io/v1/boards/{slug}/jobs?content=true')
    return [norm(name, j.get('title'), j.get('absolute_url'),
                 (j.get('location') or {}).get('name'), j.get('content', ''),
                 j.get('updated_at') or j.get('first_published', ''))
            for j in d.get('jobs', [])]


def p_ashby(name, slug):
    d = get(f'https://api.ashbyhq.com/posting-api/job-board/{slug}')
    return [norm(name, j.get('title'), j.get('jobUrl'), j.get('location'),
                 j.get('descriptionPlain', ''), (j.get('publishedAt') or ''))
            for j in d.get('jobs', [])]


def p_lever(name, slug):
    d = get(f'https://api.lever.co/v0/postings/{slug}?mode=json')
    return [norm(name, j.get('text'), j.get('hostedUrl'),
                 (j.get('categories') or {}).get('location'),
                 j.get('descriptionPlain', ''),
                 __import__('datetime').datetime.utcfromtimestamp(j['createdAt']/1000).isoformat()
                 if j.get('createdAt') else '') for j in d]


def p_workable(name, slug):
    d = get(f'https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true')
    out = []
    for j in d.get('jobs', []):
        loc = ', '.join(x for x in [j.get('city'), j.get('country')] if x)
        out.append(norm(name, j.get('title'), j.get('url') or j.get('shortlink'),
                        loc, j.get('description', ''), j.get('published', '')))
    return out


def p_recruitee(name, slug):
    d = get(f'https://{slug}.recruitee.com/api/offers/')
    return [norm(name, j.get('title'), j.get('careers_url'),
                 j.get('location') or j.get('city'), j.get('description', ''),
                 j.get('published_at', '')) for j in d.get('offers', [])]


def p_smartrecruiters(name, slug):
    d = get(f'https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100')
    out = []
    for j in d.get('content', []):
        lo = j.get('location') or {}
        loc = ', '.join(x for x in [lo.get('city'), lo.get('country')] if x)
        if lo.get('remote'):
            loc = (loc + ', Remote').lstrip(', ')
        out.append(norm(name, j.get('name'),
                        f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}", loc))
    return out


PROVIDERS = {
    'greenhouse': p_greenhouse, 'greenhouse_eu': p_greenhouse_eu, 'ashby': p_ashby,
    'lever': p_lever, 'workable': p_workable, 'recruitee': p_recruitee,
    'smartrecruiters': p_smartrecruiters,
}


# ---- filtering -------------------------------------------------------------

def title_ok(title, tf):
    t = (title or '').lower()
    if any(n.lower() in t for n in tf.get('negative', [])):
        return False
    pos = tf.get('positive', [])
    return (not pos) or any(p.lower() in t for p in pos)


def location_ok(loc, lf):
    l = (loc or '').lower()
    if not l:
        return True
    if any(a.lower() in l for a in lf.get('always_allow', [])):
        return True
    if any(b.lower() in l for b in lf.get('block', [])):
        return False
    allow = lf.get('allow') or []
    return (not allow) or any(a.lower() in l for a in allow)


def remote_signal(job):
    """Cheap read on whether the posting looks genuinely remote."""
    blob = (job['location'] + ' ' + job['desc']).lower()
    if re.search(r'\b(remote[- ]?first|fully remote|work from anywhere|100% remote|worldwide)\b', blob):
        return 'REMOTE+'
    if 'hybrid' in blob or 'on-site' in blob or 'onsite' in blob:
        return 'HYBRID?'
    if 'remote' in blob:
        return 'REMOTE'
    return '-'


# ---- main ------------------------------------------------------------------

def probe(slugs):
    print('Probing which ATS each company uses...\n')
    for slug in slugs:
        hits = []
        for pname, fn in PROVIDERS.items():
            try:
                jobs = fn(slug, slug)
                if jobs:
                    hits.append(f'{pname} ({len(jobs)} jobs)')
            except Exception:
                pass
        print(f'  {slug:24s} -> {", ".join(hits) if hits else "no public API found"}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='portals.yml')
    ap.add_argument('--out', default='portal_jobs.csv')
    ap.add_argument('--probe', help='comma-separated slugs to probe for their ATS')
    ap.add_argument('--no-filter', action='store_true')
    ap.add_argument('--top', type=int, default=60)
    ap.add_argument('--max-age-days', type=int, default=0,
                    help='keep only postings published/updated within N days')
    a = ap.parse_args()

    if a.probe:
        probe([s.strip() for s in a.probe.split(',') if s.strip()])
        return

    cfg = yaml.safe_load(open(a.config, encoding='utf-8'))
    tf = cfg.get('title_filter', {})
    lf = cfg.get('location_filter', {})
    companies = [c for c in cfg.get('tracked_companies', []) if c.get('enabled', True)]

    print(f'Scanning {len(companies)} company portals...\n')
    all_jobs, failed = [], []

    def fetch(c):
        fn = PROVIDERS.get(c['provider'])
        if not fn:
            return c['name'], None, f"unknown provider {c['provider']}"
        try:
            return c['name'], fn(c['name'], c['slug']), None
        except Exception as e:
            return c['name'], None, str(e)[:60]

    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, jobs, err in ex.map(fetch, companies):
            if err:
                failed.append((name, err))
                print(f'  {name:22s} FAILED  {err}')
            else:
                all_jobs.extend(jobs)
                print(f'  {name:22s} {len(jobs):4d} jobs')

    kept = all_jobs if a.no_filter else [
        j for j in all_jobs if title_ok(j['title'], tf) and location_ok(j['location'], lf)]

    for j in kept:
        j['remote'] = remote_signal(j)
        j.pop('desc', None)

    seen, uniq = set(), []
    for j in kept:
        k = (j['company'].lower(), re.sub(r'\W+', '', j['title'].lower()))
        if k not in seen:
            seen.add(k)
            uniq.append(j)

    if a.max_age_days:
        import datetime as _dt
        cutoff = (_dt.datetime.utcnow() - _dt.timedelta(days=a.max_age_days)).strftime('%Y-%m-%d')
        uniq = [j for j in uniq if j.get('posted') and j['posted'] >= cutoff]

    uniq.sort(key=lambda j: (j.get('posted', ''), j['company']), reverse=True)

    with open(a.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['company', 'title', 'location', 'remote', 'posted', 'url'])
        w.writeheader()
        w.writerows(uniq)

    print(f'\n=== {len(all_jobs)} scanned -> {len(uniq)} matches ===')
    if failed:
        print(f'({len(failed)} portals failed -- check the slug/provider)')
    print(f'CSV -> {a.out}\n')
    for j in uniq[:a.top]:
        print(f"[{j['remote']:7s}] {j.get('posted','-'):10s} {j['title'][:46]:46s} {j['company'][:15]:15s} {j['location'][:26]}")


if __name__ == '__main__':
    main()
