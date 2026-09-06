"""Replace the audit's stylesheet with the neutral document theme.

Legacy custom-property names are kept as aliases so the inline SVG charts,
which reference var(--accent) / var(--crit) / var(--muted) and friends,
keep resolving without touching the markup.

    python src/restyle_audit.py
"""
import io
import re
import sys

NEW_STYLE = """<style>
/* ============================================================
   ZEIT - neutral document theme (matches the System Handbook)
   Legacy token names are aliased so inline SVG keeps working.
   ============================================================ */
:root{
  --bg:#ffffff; --bg-alt:#f5f5f7; --bg-sunk:#fafafc;
  --text:#1d1d1f; --text-2:#424245; --text-3:#6e6e73;
  --rule:#d2d2d7; --rule-soft:#e8e8ed;
  --link:#0066cc;
  --sev-crit:#b3261e; --sev-high:#a15c00; --sev-med:#6e6e73; --sev-ok:#1d7a3e;
  --shadow:0 1px 3px rgba(0,0,0,.07), 0 8px 28px rgba(0,0,0,.06);
  --radius:12px;
  --ink:var(--text); --ink2:var(--text-2); --muted:var(--text-3);
  --ground:var(--bg); --surface:var(--bg); --sunk:var(--bg-alt);
  --line:var(--rule-soft); --line-strong:var(--rule);
  --accent:var(--text); --accent-ink:var(--text); --accent-soft:var(--bg-alt);
  --crit:var(--sev-crit); --crit-soft:var(--bg-alt);
  --high:var(--sev-high); --high-soft:var(--bg-alt);
  --med:var(--sev-med); --med-soft:var(--bg-alt);
  --keep:var(--sev-ok); --keep-soft:var(--bg-alt);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#000; --bg-alt:#1d1d1f; --bg-sunk:#161617;
    --text:#f5f5f7; --text-2:#d2d2d7; --text-3:#86868b;
    --rule:#424245; --rule-soft:#2c2c2e;
    --link:#2997ff;
    --sev-crit:#ff6b5e; --sev-high:#e3a34a; --sev-med:#86868b; --sev-ok:#4cc76a;
    --shadow:0 1px 3px rgba(0,0,0,.5), 0 8px 28px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --bg:#000; --bg-alt:#1d1d1f; --bg-sunk:#161617;
  --text:#f5f5f7; --text-2:#d2d2d7; --text-3:#86868b;
  --rule:#424245; --rule-soft:#2c2c2e;
  --link:#2997ff;
  --sev-crit:#ff6b5e; --sev-high:#e3a34a; --sev-med:#86868b; --sev-ok:#4cc76a;
  --shadow:0 1px 3px rgba(0,0,0,.5), 0 8px 28px rgba(0,0,0,.4);
}

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:17px;line-height:1.53;letter-spacing:-.003em;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.wrap{max-width:1120px;margin:0 auto;padding:0 32px 120px}
.col{max-width:74ch}
h1,h2,h3,h4,.ui{font-family:inherit}
.mono,code,kbd,td.num,.tag,.rule{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}

.mast{padding:76px 0 40px}
.eyebrow{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);
  font-weight:600;margin:0 0 18px}
h1{font-size:clamp(40px,6.4vw,68px);line-height:1.05;font-weight:700;letter-spacing:-.028em;
  margin:0 0 20px;text-wrap:balance}
.dek{font-size:21px;color:var(--text-2);margin:0;max-width:60ch;line-height:1.42;letter-spacing:-.012em}
.mast-meta{display:flex;flex-wrap:wrap;gap:10px 34px;margin-top:30px;padding-top:24px;
  border-top:1px solid var(--rule-soft);font-size:13px;color:var(--text-3)}
.mast-meta b{color:var(--text-2);font-weight:600}

.verdict{margin:34px 0 0;background:var(--bg-alt);border-radius:var(--radius);overflow:hidden}
.verdict-head{padding:24px 28px 20px;display:flex;flex-wrap:wrap;align-items:baseline;gap:16px}
.verdict-head .stamp{font-size:12px;font-weight:600;letter-spacing:.06em;padding:6px 12px;
  background:var(--text);color:var(--bg);border-radius:6px;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.verdict-head p{margin:0;font-size:17px;color:var(--text-2);flex:1;min-width:280px;line-height:1.45}
.tallies{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  border-top:1px solid var(--rule-soft)}
.tally{padding:20px 28px 22px;border-right:1px solid var(--rule-soft)}
.tally:last-child{border-right:none}
.tally .n{font-size:38px;font-weight:700;line-height:1;display:block;
  font-variant-numeric:tabular-nums;letter-spacing:-.026em}
.tally .lb{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);
  margin-top:9px;display:block;font-weight:600}
.tally.c .n{color:var(--sev-crit)} .tally.h .n{color:var(--sev-high)}
.tally.m .n{color:var(--text)} .tally.k .n{color:var(--sev-ok)}

section{padding-top:88px}
.sec-head{display:flex;align-items:baseline;gap:16px;margin-bottom:8px}
.sec-num{font-size:13px;font-weight:600;color:var(--text-3);padding-top:8px;white-space:nowrap;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
h2{font-size:clamp(28px,3.6vw,40px);font-weight:700;letter-spacing:-.024em;margin:0;
  line-height:1.1;text-wrap:balance}
.sec-sub{color:var(--text-3);font-size:17px;margin:10px 0 32px;max-width:66ch;line-height:1.45}
h3{font-size:24px;font-weight:600;margin:48px 0 12px;letter-spacing:-.018em;text-wrap:balance}
h4{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);
  margin:30px 0 10px}
p{margin:0 0 17px}
strong{font-weight:600;color:var(--text)}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
a:focus-visible{outline:2px solid var(--link);outline-offset:3px;border-radius:2px}
code{font-size:.86em;background:var(--bg-alt);padding:2px 6px;border-radius:5px;color:var(--text-2)}
ul,ol{margin:0 0 17px;padding-left:24px}
li{margin-bottom:9px}
ul.tight li{margin-bottom:5px}

.toc{background:var(--bg-alt);border-radius:var(--radius);padding:26px 28px;margin-top:34px}
.toc ol{list-style:none;padding:0;margin:0;columns:2;column-gap:44px;font-size:15.5px}
.toc li{margin-bottom:11px;break-inside:avoid;display:flex;gap:12px}
.toc .k{font-size:12px;color:var(--text-3);padding-top:2px;flex:0 0 24px;font-weight:500;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.toc a{color:var(--text);text-decoration:none}
.toc a:hover{color:var(--link);text-decoration:underline}
@media(max-width:640px){.toc ol{columns:1}}

.tblwrap{overflow-x:auto;margin:22px 0 30px;border-top:1px solid var(--text);
  border-bottom:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-size:15px;min-width:520px}
th{font-size:11.5px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--text-3);
  text-align:left;padding:13px 16px 12px;border-bottom:1px solid var(--rule);white-space:nowrap}
td{padding:14px 16px;border-bottom:1px solid var(--rule-soft);vertical-align:top;
  font-size:15px;line-height:1.45;color:var(--text-2)}
tr:last-child td{border-bottom:none}
tbody tr:hover td{background:var(--bg-sunk)}
td.num{text-align:right;font-variant-numeric:tabular-nums;font-size:13.5px;white-space:nowrap}
td.name{font-weight:600;color:var(--text)}
.fail{color:var(--sev-crit);font-weight:600}
.pass{color:var(--sev-ok);font-weight:600}

.finding{border-top:1px solid var(--rule);margin-bottom:0;padding-bottom:10px}
.finding:first-of-type{border-top:1px solid var(--text)}
.f-head{padding:30px 0 6px}
.f-tags{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:13px}
.tag{font-size:10.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
  padding:4px 10px;border-radius:5px;background:var(--bg-alt);color:var(--text-3)}
.tag.crit{color:var(--bg);background:var(--sev-crit)}
.tag.high{color:var(--bg);background:var(--sev-high)}
.tag.med{color:var(--text-2);background:var(--bg-alt)}
.tag.id{color:var(--text-3);background:transparent;box-shadow:inset 0 0 0 1px var(--rule);
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.tag.verified{color:var(--sev-ok);background:var(--bg-alt)}
.f-head h3{margin:0;font-size:26px;font-weight:600;line-height:1.18;letter-spacing:-.022em}
.f-body{padding:0 0 22px;max-width:78ch}
.f-body>p:first-child{margin-top:0}
.f-do{margin:22px 0 0;padding:20px 24px;background:var(--bg-alt);border-radius:var(--radius)}
.f-do .lb{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);
  display:block;margin-bottom:9px;font-weight:600}
.f-do p{margin:0;font-size:16px}
.f-do p+p{margin-top:12px}

blockquote{margin:20px 0;padding:4px 0 4px 22px;box-shadow:inset 2px 0 0 var(--rule);
  color:var(--text-2);font-size:16.5px;line-height:1.5}
blockquote cite{display:block;font-style:normal;font-size:12.5px;color:var(--text-3);margin-top:10px;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}

.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px;margin:24px 0 10px}
.chart{background:var(--bg-alt);border-radius:var(--radius);padding:22px 22px 16px}
.chart h4{margin:0 0 6px;color:var(--text);font-size:12px}
.chart .cap{font-size:13.5px;color:var(--text-3);margin:12px 0 0;line-height:1.45}
svg{display:block;width:100%;height:auto}
.svg-t{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  font-size:10px;fill:var(--text-3)}
.svg-t.strong{fill:var(--text-2);font-weight:500}
.svg-lab{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  font-size:11px;font-weight:600}

.chain{background:var(--bg-alt);border-radius:var(--radius);padding:24px 26px;margin:24px 0 30px;
  overflow-x:auto}
.chain-row{display:flex;gap:6px;min-width:640px}
.blk{flex:1;background:var(--bg);border-radius:8px;padding:12px 8px;text-align:center;
  position:relative;min-width:0}
.blk .n{font-size:10px;color:var(--text-3);display:block;font-weight:600;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.blk .t{font-size:13px;font-weight:600;display:block;margin-top:4px;line-height:1.2;color:var(--text)}
.blk .s{font-size:9.5px;color:var(--text-3);display:block;margin-top:5px;line-height:1.3;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.blk.ai{box-shadow:inset 0 0 0 2px var(--text)}
.blk.flag{box-shadow:inset 0 0 0 2px var(--sev-crit)}
.blk.flag .n{color:var(--sev-crit)}
.chain-note{font-size:12.5px;color:var(--text-3);margin:16px 0 0;line-height:1.6}
.chain-note b{color:var(--sev-crit);font-weight:600}

.callout{background:var(--bg-alt);border-radius:var(--radius);padding:22px 26px;margin:26px 0;
  max-width:78ch}
.callout p:last-child{margin-bottom:0}
.callout p{font-size:16px}
.callout .lb{font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-3);
  font-weight:600;display:block;margin-bottom:10px}

.keeps{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px;margin:24px 0 0}
.keep-item{background:var(--bg-alt);border-radius:var(--radius);padding:20px 22px}
.keep-item .h{font-weight:600;font-size:16.5px;margin:0 0 7px;color:var(--text);letter-spacing:-.012em}
.keep-item p{margin:0;font-size:14.8px;color:var(--text-2);line-height:1.47}

.steps{counter-reset:s;list-style:none;padding:0;margin:26px 0 0}
.steps li{counter-increment:s;position:relative;padding:0 0 26px 52px;margin:0}
.steps li::before{content:counter(s);position:absolute;left:0;top:0;width:30px;height:30px;
  background:var(--text);color:var(--bg);border-radius:50%;font-size:13px;font-weight:600;
  display:grid;place-items:center;
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.steps li::after{content:"";position:absolute;left:14.5px;top:34px;bottom:2px;width:1px;
  background:var(--rule)}
.steps li:last-child{padding-bottom:0}
.steps li:last-child::after{display:none}
.steps .h{font-weight:600;font-size:18px;display:block;margin-bottom:4px;line-height:1.3;
  letter-spacing:-.014em;color:var(--text)}
.steps p{margin:0;font-size:16px;color:var(--text-2)}

footer{margin-top:100px;padding-top:30px;border-top:1px solid var(--rule);font-size:13px;
  color:var(--text-3);line-height:1.65;max-width:80ch}
footer p{margin:0 0 12px}

@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media(max-width:700px){
  body{font-size:16.5px}
  .wrap{padding:0 20px 80px}
  .mast{padding:48px 0 32px}
  section{padding-top:64px}
  .tally{border-right:none;border-bottom:1px solid var(--rule-soft)}
  .keeps{grid-template-columns:1fr}
}
</style>"""

path = "zeit-audit.html"
src = io.open(path, encoding="utf-8").read()

out = re.sub(r"<style>.*?</style>", lambda m: NEW_STYLE, src, count=1, flags=re.S)
if out == src or "--sev-crit" not in out:
    sys.exit("style block was not replaced")

# Primary chart series moves to near-black; the target line keeps its red.
out = out.replace('stroke="var(--accent)"', 'stroke="var(--text)"')
out = out.replace('fill="var(--accent)"', 'fill="var(--text)"')

# System typeface now, so the webfont link is dead weight.
out = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", out)
out = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis[^>]*>\s*', "", out)

io.open(path, "w", encoding="utf-8").write(out)
print("audit restyled:", len(out), "bytes")
