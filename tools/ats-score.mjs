#!/usr/bin/env node
/**
 * ats-score.mjs — keyword-match score between a job description and a CV.
 *
 * Models what a keyword-based ATS actually does: build the requirement
 * vocabulary from the posting, then measure how much of it the CV surfaces.
 * Terms in the requirements/qualifications block count double, because that is
 * where screening rules are typically drawn from.
 *
 * Deliberately NOT a fit score. It says nothing about whether the job is a good
 * idea — only how legible this CV is to keyword screening for this posting.
 *
 *   node ats-score.mjs <jd.txt> <cv.md> [--json]
 *   node ats-score.mjs --all            # every applications/<folder> with posting.txt and cv.md
 */
import { readFileSync, existsSync, readdirSync } from 'node:fs';

/** Synonym groups: any surface form in a group satisfies any other. */
const SYN = [
  ['revenue operations','revops','revenue ops'],
  ['sales operations','sales ops'],
  ['go-to-market','gtm','go to market'],
  ['business intelligence','bi'],
  ['financial planning and analysis','fp&a','financial planning'],
  ['customer relationship management','crm'],
  ['salesforce','sfdc','salesforce.com'],
  ['power bi','powerbi'],
  ['data modeling','data modelling','data models'],
  ['data hygiene','data quality','system hygiene'],
  ['forecasting','forecast','forecasts'],
  ['pipeline management','pipeline'],
  ['funnel analysis','funnel'],
  ['capacity planning','capacity forecasting','resource modeling','resource modelling'],
  ['customer lifecycle','lifecycle'],
  ['contribution margin','margin'],
  ['unit economics'],
  ['quote-to-cash','quote to cash','cpq'],
  ['deal desk'],
  ['market expansion','expansion strategy'],
  ['due diligence'],
  ['competitive analysis','competitive intelligence','competitor analysis'],
  ['market share'],
  ['segmentation','segments'],
  ['cross-functional','cross functional'],
  ['stakeholder management','stakeholders','stakeholder'],
  ['process design','process mapping','workflow design','operational frameworks'],
  ['enablement','sales enablement'],
  ['documentation','document'],
  ['dashboard','dashboards','dashboarding'],
  ['reporting','reports'],
  ['kpi','kpis','metrics','performance metrics'],
  ['erp','sap','s/4hana','sap s/4hana'],
  ['sql'],['python'],['excel'],['tableau'],['qlik'],['looker'],['domo'],['dbt'],
  ['snowflake'],['bigquery'],['jira'],['asana'],['hubspot'],['netsuite'],['anaplan'],
  ['pricing','pricing strategy'],['discounting','discounts'],
  ['commission','compensation plan','incentive'],
  ['quota','quotas'],['territory','territories'],
  ['churn','attrition'],['retention'],['renewals','renewal'],
  ['arr','mrr','acv','recurring revenue'],
  ['conversion','conversion rate'],['attribution'],
  ['lead generation','demand generation','lead gen'],
  ['saas','b2b saas'],['b2b'],['subscription'],
  ['customer success','client success'],
  ['account management','account manager'],
  ['partnerships','partner'],
  ['budget','budgeting'],['variance'],['headcount','staffing'],
  ['analytics','analysis','analytical'],
  ['commercial'],['operations'],['strategy'],
  ['onboarding'],['governance'],['automation'],
];
const CANON = new Map();
for (const g of SYN) for (const s of g) CANON.set(s, g[0]);
const TERMS = [...CANON.keys()].sort((a,b)=>b.length-a.length);

const norm = s => (s||'').toLowerCase().replace(/[’']/g,"'").replace(/\s+/g,' ');

/** Split a posting into (requirements, rest) so requirements can be weighted. */
function splitReq(text){
  const t = norm(text);
  const m = t.search(/\b(requirements|qualifications|what you bring|who you are|what we.re looking for|you have|about you|must have|your profile|skills and experience)\b/);
  return m < 0 ? { req:'', rest:t } : { req:t.slice(m), rest:t.slice(0,m) };
}

const found = (hay, term) => new RegExp(`(?<![a-z0-9])${term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}(?![a-z0-9])`,'i').test(hay);

export function score(jdText, cvText){
  const { req, rest } = splitReq(jdText);
  const cv = norm(cvText);
  const weights = new Map();           // canonical term -> weight from JD
  for (const term of TERMS){
    const canon = CANON.get(term);
    let w = 0;
    if (found(req, term))  w = 2;
    else if (found(rest, term)) w = 1;
    if (w) weights.set(canon, Math.max(weights.get(canon)||0, w));
  }
  const matched=[], missing=[];
  let got=0, total=0;
  for (const [canon, w] of weights){
    total += w;
    const forms = SYN.find(g=>g[0]===canon) || [canon];
    if (forms.some(f=>found(cv,f))) { got += w; matched.push({term:canon,w}); }
    else missing.push({term:canon,w});
  }
  const coverage = total ? got/total : 0;
  // 0.30 coverage -> 1.0 ; 0.85 coverage -> 5.0, clamped.
  const raw = 1 + (coverage-0.30)*(4/0.55);
  const out = Math.max(0, Math.min(5, raw));
  return {
    score: Math.round(out*10)/10,
    coverage: Math.round(coverage*1000)/10,
    matched_weight: got, total_weight: total,
    matched: matched.sort((a,b)=>b.w-a.w).map(x=>x.term),
    missing: missing.sort((a,b)=>b.w-a.w).map(x=>x.term),
    critical_missing: missing.filter(x=>x.w===2).map(x=>x.term),
  };
}

if (process.argv[1]?.endsWith('ats-score.mjs')){
  const a = process.argv.slice(2);
  if (a[0]==='--all'){
    // every applications/<folder>/ that has both posting.txt and cv.md
    const dirs = existsSync('applications') ? readdirSync('applications', { withFileTypes: true })
      .filter(d=>d.isDirectory()).map(d=>d.name) : [];
    const res = dirs.filter(d=>existsSync(`applications/${d}/posting.txt`) && existsSync(`applications/${d}/cv.md`))
      .map(d=>({ job: d, ...score(readFileSync(`applications/${d}/posting.txt`,'utf8'), readFileSync(`applications/${d}/cv.md`,'utf8')) }));
    console.log(JSON.stringify(res,null,1));
  } else if (a.length>=2){
    console.log(JSON.stringify(score(readFileSync(a[0],'utf8'), readFileSync(a[1],'utf8')),null,1));
  } else { console.log('Usage: node ats-score.mjs <jd.txt> <cv.md> | --all'); process.exit(1); }
}
