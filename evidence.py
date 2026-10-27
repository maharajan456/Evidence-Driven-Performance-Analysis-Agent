import hashlib, json, time
from pathlib import Path
import requests

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def collect_http_samples(url, out_dir, count=30, timeout=3):
    out_dir.mkdir(parents=True, exist_ok=True); samples=[]
    for i in range(count):
        start=time.perf_counter()
        try:
            r=requests.get(url.rstrip("/")+"/work", timeout=timeout)
            samples.append({"sample":i+1,"status_code":r.status_code,"latency_ms":round((time.perf_counter()-start)*1000,4),"ok":r.ok})
        except requests.RequestException as e:
            samples.append({"sample":i+1,"status_code":None,"latency_ms":round((time.perf_counter()-start)*1000,4),"ok":False,"error":type(e).__name__})
    p=out_dir/"http-samples.json"; write_json(p,{"url":url,"count":count,"samples":samples}); return p

def build_manifest(input_dir, manifest_path):
    input_dir.mkdir(parents=True, exist_ok=True); evidence=[]
    for i,p in enumerate(sorted(x for x in input_dir.rglob("*") if x.is_file()),1):
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        evidence.append({"evidence_id":f"E{i:03d}","file":str(p.relative_to(input_dir)),"sha256":h,"bytes":p.stat().st_size})
    manifest={"created_unix":int(time.time()),"evidence":evidence}; write_json(manifest_path,manifest); return manifest

def read_evidence(input_dir, manifest, limit=10000):
    parts=[]
    for item in manifest["evidence"]:
        body=(input_dir/item["file"]).read_text(encoding="utf-8",errors="replace")[:limit]
        parts.append(f'--- {item["evidence_id"]} | {item["file"]} ---\n{body}')
    return "\n\n".join(parts) or "No input evidence files were found."
