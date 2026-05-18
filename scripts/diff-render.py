#!/usr/bin/env python3
"""oasdiff diff JSON → 커스텀 HTML 렌더러"""

import json
import sys
import subprocess
from datetime import datetime

METHOD_COLORS = {
    'GET':     '#22c55e',
    'POST':    '#3b82f6',
    'PUT':     '#f59e0b',
    'PATCH':   '#8b5cf6',
    'DELETE':  '#ef4444',
    'HEAD':    '#6b7280',
    'OPTIONS': '#6b7280',
}

# ── spec 유틸 ─────────────────────────────────────────────────────────────────

def load_spec(path):
    with open(path) as f:
        return json.load(f)

def resolve_ref(ref, spec, depth=0):
    if depth > 6 or not ref.startswith('#/'):
        return {}
    parts = ref[2:].split('/')
    obj = spec
    for part in parts:
        obj = obj.get(part, {})
    if isinstance(obj, dict) and '$ref' in obj:
        return resolve_ref(obj['$ref'], spec, depth + 1)
    return obj

def resolve_schema(schema, spec, depth=0):
    if depth > 6:
        return schema
    if not isinstance(schema, dict):
        return {}
    if '$ref' in schema:
        return resolve_schema(resolve_ref(schema['$ref'], spec), spec, depth + 1)
    return schema

def run_oasdiff(old, new):
    r = subprocess.run(
        ['oasdiff', 'diff', old, new, '-f', 'json'],
        capture_output=True, text=True
    )
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        return {}

# ── 공통 HTML 조각 ────────────────────────────────────────────────────────────

def method_badge(method):
    color = METHOD_COLORS.get(method.upper(), '#6b7280')
    return f'<span class="badge-method" style="background:{color}">{method.upper()}</span>'

def schema_table(schema, spec):
    schema = resolve_schema(schema, spec)
    props = schema.get('properties', {})
    required = schema.get('required', [])
    if not props:
        t = schema.get('type', 'object')
        return f'<span class="tag-type">{t}</span>'

    rows = ''
    for name, prop in props.items():
        prop = resolve_schema(prop, spec)
        t = prop.get('type', '')
        if not t and '$ref' in prop:
            t = prop['$ref'].split('/')[-1]
        fmt = prop.get('format', '')
        type_str = f'{t}({fmt})' if fmt else (t or 'object')
        desc = prop.get('description', '')
        ex = prop.get('example', '')
        desc_html = f'{desc} <span class="example">예: {ex}</span>' if ex else desc
        req_mark = '<span class="required">✓</span>' if name in required else ''
        rows += f'''<tr>
          <td><code>{name}</code></td>
          <td><span class="tag-type">{type_str}</span></td>
          <td class="center">{req_mark}</td>
          <td class="muted">{desc_html}</td>
        </tr>'''
    return f'''<table class="tbl">
      <thead><tr><th>필드</th><th>타입</th><th>필수</th><th>설명</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>'''

# ── 신규 endpoint 렌더 ────────────────────────────────────────────────────────

def render_new_endpoint(path, method, op, spec):
    summary = op.get('summary', '')
    inner = ''

    # Parameters
    params = op.get('parameters', [])
    if params:
        rows = ''
        for p in params:
            s = resolve_schema(p.get('schema', {}), spec)
            t = s.get('type', 'string')
            fmt = s.get('format', '')
            type_str = f'{t}({fmt})' if fmt else t
            req = '<span class="required">✓</span>' if p.get('required') else ''
            desc = p.get('description', '')
            rows += f'''<tr>
              <td><code>{p["name"]}</code></td>
              <td><span class="tag-in">{p["in"]}</span></td>
              <td><span class="tag-type">{type_str}</span></td>
              <td class="center">{req}</td>
              <td class="muted">{desc}</td>
            </tr>'''
        inner += f'''<div class="ep-section">
          <div class="ep-section-title">Parameters</div>
          <table class="tbl">
            <thead><tr><th>이름</th><th>위치</th><th>타입</th><th>필수</th><th>설명</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>'''

    # Request Body
    rb = op.get('requestBody', {})
    if rb:
        parts = ''
        for ct, cv in rb.get('content', {}).items():
            s = resolve_schema(cv.get('schema', {}), spec)
            parts += f'<div class="media-type">{ct}</div>{schema_table(s, spec)}'
        inner += f'<div class="ep-section"><div class="ep-section-title">Request Body</div>{parts}</div>'

    # Responses
    responses = op.get('responses', {})
    if responses:
        parts = ''
        for code, resp in sorted(responses.items()):
            cls = 'success' if str(code).startswith('2') else 'error'
            desc = resp.get('description', '')
            parts += f'<div class="status-badge {cls}">{code} {desc}</div>'
            for ct, cv in resp.get('content', {}).items():
                s = resolve_schema(cv.get('schema', {}), spec)
                parts += f'<div class="media-type">{ct}</div>{schema_table(s, spec)}'
        inner += f'<div class="ep-section"><div class="ep-section-title">Responses</div>{parts}</div>'

    return f'''<div class="ep-card ep-new">
      <div class="ep-header">
        {method_badge(method)}
        <span class="ep-path">{path}</span>
        <span class="ep-summary">{summary}</span>
      </div>
      <div class="ep-body">{inner}</div>
    </div>'''

# ── 수정된 endpoint 렌더 ──────────────────────────────────────────────────────

def render_schema_diff(diff, prefix=''):
    parts = ''
    # type 변경
    if 'type' in diff:
        td = diff['type']
        if isinstance(td, dict):
            frm = ', '.join(td.get('deleted', []))
            to  = ', '.join(td.get('added', []))
            parts += f'<div class="diff added">+ {prefix}type: <code>{to}</code></div>'
            parts += f'<div class="diff deleted">- {prefix}type: <code>{frm}</code></div>'
    # format 변경
    if 'format' in diff:
        fd = diff['format']
        if isinstance(fd, dict) and 'from' in fd:
            parts += f'<div class="diff modified">~ {prefix}format: <code>{fd["from"]}</code> → <code>{fd["to"]}</code></div>'
    # required 변경
    req = diff.get('required', {})
    for r in req.get('added', []):
        parts += f'<div class="diff added">+ {prefix}<code>{r}</code> required 추가</div>'
    for r in req.get('deleted', []):
        parts += f'<div class="diff deleted">- {prefix}<code>{r}</code> required 삭제</div>'
    # properties 변경
    props = diff.get('properties', {})
    for p in props.get('added', []):
        parts += f'<div class="diff added">+ {prefix}property <code>{p}</code> 추가</div>'
    for p in props.get('deleted', []):
        parts += f'<div class="diff deleted">- {prefix}property <code>{p}</code> 삭제</div>'
    for name, sub in props.get('modified', {}).items():
        parts += render_schema_diff(sub, prefix=f'{name}.')
    return parts

def render_content_diff(content_diff):
    parts = ''
    for ct, cv in content_diff.get('modified', {}).items():
        schema_diff = cv.get('schema', {})
        parts += render_schema_diff(schema_diff)
    return parts

def render_modified_endpoint(path, method, op_diff):
    inner = ''

    # Parameters
    if 'parameters' in op_diff:
        pd = op_diff['parameters']
        parts = ''
        for loc, names in pd.get('added', {}).items():
            for n in names:
                parts += f'<div class="diff added">+ [{loc}] <code>{n}</code> 추가</div>'
        for loc, names in pd.get('deleted', {}).items():
            for n in names:
                parts += f'<div class="diff deleted">- [{loc}] <code>{n}</code> 삭제</div>'
        for loc, fields in pd.get('modified', {}).items():
            for name, changes in fields.items():
                sub = render_schema_diff(changes.get('schema', changes), prefix=f'{name}.')
                parts += sub or f'<div class="diff modified">~ [{loc}] <code>{name}</code> 변경</div>'
        if parts:
            inner += f'<div class="ep-section"><div class="ep-section-title">Parameters</div>{parts}</div>'

    # Request Body
    if 'requestBody' in op_diff:
        parts = render_content_diff(op_diff['requestBody'].get('content', {}))
        if parts:
            inner += f'<div class="ep-section"><div class="ep-section-title">Request Body</div>{parts}</div>'

    # Responses
    if 'responses' in op_diff:
        rd = op_diff['responses']
        parts = ''
        for code in rd.get('added', []):
            parts += f'<div class="diff added">+ {code} 응답 추가</div>'
        for code in rd.get('deleted', []):
            parts += f'<div class="diff deleted">- {code} 응답 삭제</div>'
        for code, rv in rd.get('modified', {}).items():
            cls = 'success' if str(code).startswith('2') else 'error'
            content_html = render_content_diff(rv.get('content', {}))
            headers = rv.get('headers', {})
            hdr_html = ''
            for h in headers.get('added', []):
                hdr_html += f'<div class="diff added">+ header <code>{h}</code> 추가</div>'
            for h in headers.get('deleted', []):
                hdr_html += f'<div class="diff deleted">- header <code>{h}</code> 삭제</div>'
            if content_html or hdr_html:
                parts += f'<div class="response-group"><span class="status-badge {cls}">{code}</span>{content_html}{hdr_html}</div>'
        if parts:
            inner += f'<div class="ep-section"><div class="ep-section-title">Responses</div>{parts}</div>'

    return f'''<div class="ep-card ep-modified">
      <div class="ep-header">
        {method_badge(method)}
        <span class="ep-path">{path}</span>
      </div>
      <div class="ep-body">{inner}</div>
    </div>'''

# ── 삭제된 endpoint 렌더 ──────────────────────────────────────────────────────

def render_deleted_endpoint(path, method, summary=''):
    return f'''<div class="ep-card ep-deleted">
      <div class="ep-header">
        {method_badge(method)}
        <span class="ep-path">{path}</span>
        <span class="ep-summary muted">{summary}</span>
      </div>
    </div>'''

# ── HTML 생성 ─────────────────────────────────────────────────────────────────

CSS = '''
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f1f5f9; color: #1e293b; line-height: 1.6; font-size: 14px; }

header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
         color: white; padding: 28px 40px; }
header h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
header .sub { font-size: 12px; color: #94a3b8; }

.stats { display: flex; gap: 12px; padding: 16px 40px;
         background: white; border-bottom: 1px solid #e2e8f0; }
.stat { padding: 10px 18px; border-radius: 8px; text-align: center; min-width: 90px; }
.stat.new     { background: #f0fdf4; border: 1px solid #bbf7d0; }
.stat.deleted { background: #fef2f2; border: 1px solid #fecaca; }
.stat.modified{ background: #fffbeb; border: 1px solid #fde68a; }
.stat .n { font-size: 26px; font-weight: 700; }
.stat.new      .n { color: #16a34a; }
.stat.deleted  .n { color: #dc2626; }
.stat.modified .n { color: #d97706; }
.stat .lbl { font-size: 11px; color: #64748b; }

.wrap { max-width: 960px; margin: 0 auto; padding: 28px 20px; }

.grp-header { display: flex; align-items: center; gap: 8px; margin: 28px 0 12px; }
.grp-header h2 { font-size: 16px; font-weight: 700; }
.grp-badge { padding: 1px 9px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.grp-badge.new      { background: #dcfce7; color: #16a34a; }
.grp-badge.deleted  { background: #fee2e2; color: #dc2626; }
.grp-badge.modified { background: #fef3c7; color: #d97706; }

.ep-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px;
           margin-bottom: 10px; overflow: hidden; }
.ep-card.ep-new      { border-left: 4px solid #22c55e; }
.ep-card.ep-deleted  { border-left: 4px solid #ef4444; opacity: 0.75; }
.ep-card.ep-modified { border-left: 4px solid #f59e0b; }

.ep-header { display: flex; align-items: center; gap: 10px; padding: 12px 16px; }
.badge-method { padding: 3px 9px; border-radius: 5px; color: white;
                font-size: 11px; font-weight: 700; letter-spacing: 0.4px;
                min-width: 60px; text-align: center; }
.ep-path    { font-family: monospace; font-size: 13px; font-weight: 600; }
.ep-summary { font-size: 12px; color: #64748b; margin-left: auto; }

.ep-body { padding: 0 16px 14px; border-top: 1px solid #f1f5f9; }
.ep-section { margin-top: 12px; }
.ep-section-title { font-size: 11px; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.7px; color: #94a3b8; margin-bottom: 6px; }

.tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
.tbl th { text-align: left; padding: 5px 8px; background: #f8fafc;
          border-bottom: 1px solid #e2e8f0; font-size: 11px;
          text-transform: uppercase; letter-spacing: 0.4px; color: #64748b; }
.tbl td { padding: 6px 8px; border-bottom: 1px solid #f8fafc; vertical-align: top; }
.tbl tr:last-child td { border-bottom: none; }
.center { text-align: center; }

.tag-type { background: #eff6ff; color: #2563eb; padding: 1px 5px;
            border-radius: 4px; font-size: 11px; font-family: monospace; }
.tag-in   { background: #f5f3ff; color: #7c3aed; padding: 1px 5px;
            border-radius: 4px; font-size: 10px; }
.required { color: #16a34a; font-weight: 700; }
.muted    { color: #94a3b8; font-size: 12px; }
.example  { color: #94a3b8; font-size: 11px; }
code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px;
       font-size: 11px; font-family: monospace; color: #0f172a; }

.media-type { font-size: 11px; color: #64748b; font-family: monospace;
              margin: 6px 0 3px; }

.diff { padding: 4px 10px; border-radius: 5px; font-size: 12px; margin: 3px 0; }
.diff.added    { background: #f0fdf4; color: #15803d; }
.diff.deleted  { background: #fef2f2; color: #b91c1c; }
.diff.modified { background: #fffbeb; color: #92400e; }

.status-badge { display: inline-block; padding: 2px 7px; border-radius: 4px;
                font-size: 11px; font-weight: 600; margin: 3px 0 5px; }
.status-badge.success { background: #dcfce7; color: #16a34a; }
.status-badge.error   { background: #fee2e2; color: #dc2626; }
.response-group { margin: 6px 0; }

.empty { color: #94a3b8; font-size: 13px; padding: 16px;
         text-align: center; background: white; border-radius: 8px;
         border: 1px dashed #e2e8f0; }

footer { text-align: center; padding: 20px; color: #94a3b8;
         font-size: 11px; margin-top: 20px; }
'''

def generate(old_path, new_path, output_path):
    diff     = run_oasdiff(old_path, new_path)
    old_spec = load_spec(old_path)
    new_spec = load_spec(new_path)

    title    = new_spec.get('info', {}).get('title', 'API')
    paths_d  = diff.get('paths', {})

    added_paths   = paths_d.get('added', [])
    deleted_paths = paths_d.get('deleted', [])
    modified_paths = paths_d.get('modified', {})

    new_html = deleted_html = modified_html = ''
    new_cnt = deleted_cnt = modified_cnt = 0

    # ── 신규 paths ──────────────────────────────────────────────────────────
    for path in added_paths:
        path_obj = new_spec.get('paths', {}).get(path, {})
        for m, op in path_obj.items():
            if m in ('get','post','put','patch','delete','head','options'):
                new_html += render_new_endpoint(path, m.upper(), op, new_spec)
                new_cnt += 1

    # ── modified paths 내 added/deleted/modified operations ─────────────────
    for path, path_diff in modified_paths.items():
        ops = path_diff.get('operations', {})

        for m in ops.get('deleted', []):
            op = old_spec.get('paths', {}).get(path, {}).get(m.lower(), {})
            deleted_html += render_deleted_endpoint(path, m, op.get('summary', ''))
            deleted_cnt += 1

        for m in ops.get('added', []):
            op = new_spec.get('paths', {}).get(path, {}).get(m.lower(), {})
            new_html += render_new_endpoint(path, m, op, new_spec)
            new_cnt += 1

        for m, op_diff in ops.get('modified', {}).items():
            modified_html += render_modified_endpoint(path, m, op_diff)
            modified_cnt += 1

    # ── deleted paths ───────────────────────────────────────────────────────
    for path in deleted_paths:
        path_obj = old_spec.get('paths', {}).get(path, {})
        for m, op in path_obj.items():
            if m in ('get','post','put','patch','delete','head','options'):
                deleted_html += render_deleted_endpoint(path, m.upper(), op.get('summary',''))
                deleted_cnt += 1

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    old_name = old_path.split('/')[-1]
    new_name = new_path.split('/')[-1]

    def section(label, cls, cnt, content):
        body = content if content else '<div class="empty">변경사항 없음</div>'
        return f'''<div class="grp-header">
          <h2>{label}</h2>
          <span class="grp-badge {cls}">{cnt}</span>
        </div>{body}'''

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} – API Diff</title>
<style>{CSS}</style>
</head>
<body>

<header>
  <h1>{title} — API Change Log</h1>
  <div class="sub">생성: {now} &nbsp;|&nbsp; {old_name} → {new_name}</div>
</header>

<div class="stats">
  <div class="stat new">    <div class="n">{new_cnt}</div>     <div class="lbl">New APIs</div></div>
  <div class="stat deleted"><div class="n">{deleted_cnt}</div> <div class="lbl">Deleted APIs</div></div>
  <div class="stat modified"><div class="n">{modified_cnt}</div><div class="lbl">Modified APIs</div></div>
</div>

<div class="wrap">
  {section("신규 API", "new", new_cnt, new_html)}
  {section("삭제된 API", "deleted", deleted_cnt, deleted_html)}
  {section("변경된 API", "modified", modified_cnt, modified_html)}
</div>

<footer>Generated by oasdiff-html-renderer · {now}</footer>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✓ {output_path}')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 diff-render.py <old-spec> <new-spec> <output.html>')
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2], sys.argv[3])
