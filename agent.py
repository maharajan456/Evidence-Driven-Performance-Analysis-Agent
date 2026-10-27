import os, json
from pathlib import Path
import requests
from dotenv import load_dotenv
from evidence import build_manifest, read_evidence
from verify_report import verify_report
SYSTEM="""You are a cautious performance engineer. Analyze only supplied evidence. Do not invent measurements, source lines, or findings. Return ONLY JSON: {\"summary\":\"...\",\"findings\":[{\"title\":\"...\",\"diagnosis\":\"...\",\"recommendation\":\"...\",\"evidence_ids\":[\"E001\"]}],\"limitations\":[\"...\"]}. Every finding must cite existing evidence IDs. Do not claim code was changed or a fix verified unless the evidence shows it."""
def analyze(input_dir: Path, output_dir: Path, model=None):
    load_dotenv(); base=os.getenv("OLLAMA_BASE_URL","http://localhost:11434"); model=model or os.getenv("OLLAMA_MODEL","qwen3:8b")
    output_dir.mkdir(parents=True,exist_ok=True); manifest=build_manifest(input_dir,output_dir/"evidence-manifest.json")
    prompt="Review these service performance artifacts. Separate observations from hypotheses and state limitations.\nMANIFEST:\n"+json.dumps(manifest,indent=2)+"\nEVIDENCE:\n"+read_evidence(input_dir,manifest)
    r=requests.post(base.rstrip("/")+"/api/chat",json={"model":model,"stream":False,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],"options":{"temperature":0.1}},timeout=180); r.raise_for_status()
    raw=r.json()["message"]["content"]; (output_dir/"llm-raw-response.txt").write_text(raw,encoding="utf-8")
    ok,result=verify_report(raw,{x["evidence_id"] for x in manifest["evidence"]})
    if not ok:
        (output_dir/"verification-failure.txt").write_text(result,encoding="utf-8"); raise RuntimeError(result)
    out=output_dir/"verified-report.json"; out.write_text(result,encoding="utf-8"); return out
