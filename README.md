# Project - Evidence-Driven Performance Analysis Agent

## What it does
A Python workflow that collects HTTP latency samples, builds a SHA-256 evidence manifest, sends supplied evidence to a local Ollama model (Qwen3 by default), and validates the model's JSON report. Every finding must cite evidence IDs that exist in the manifest. This reduces unsupported claims, but does not prove a diagnosis is causally correct.

## Included synthetic test data
`artifacts/input/` contains synthetic HTTP samples, CPU-profile text, mutex-profile text, and a load-test summary. These are fabricated fixtures designed to exercise evidence ingestion and report validation. They are **not** measurements from the included Go service and must not be used as real benchmark results.

## Run the offline smoke test
From this directory, with the repository's Python dependencies installed:

```bash
python -c "from pathlib import Path; from evidence import build_manifest; from verify_report import verify_report; import json; p=Path('artifacts/input'); m=build_manifest(p,Path('artifacts/output/evidence-manifest.json')); ids={e['evidence_id'] for e in m['evidence']}; raw=json.dumps({'summary':'Offline smoke test','findings':[{'title':'Fixture indexed','diagnosis':'Synthetic inputs were indexed','recommendation':'Collect real profiles before diagnosis','evidence_ids':[next(iter(ids))]}],'limitations':['No LLM called; synthetic fixtures only']}); ok,result=verify_report(raw,ids); print('PASS' if ok else 'FAIL'); print(result)"
```

A passing result tests evidence-ID/schema validation only. It does not call an LLM.

## Run the full local demo
Requirements: Python 3.10+, Go 1.21+, Ollama, and the `qwen3:8b` model.

1. Install dependencies: `pip install -r requirements.txt`
2. Start Ollama and run `ollama pull qwen3:8b`
3. In one terminal, run `cd go-service && go run .`
4. In another terminal, from this project directory, run:

```bash
python run_demo.py --url http://localhost:8080 --model qwen3:8b
```

For real profiling, collect fresh pprof and load-test artifacts; document hardware, software versions, duration, concurrency, and offered request rate. Do not expose pprof endpoints publicly.

## Results from this package
- Offline evidence-manifest/report-schema smoke test: **PASS**.
- Evidence files indexed in the saved smoke test: see `artifacts/output/offline_test_summary.json`.
- Full LLM analysis and live Go-service benchmarking: **not run** as part of this offline test.
