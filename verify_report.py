import json
from pydantic import BaseModel, Field, ValidationError
class Finding(BaseModel):
    title: str
    diagnosis: str
    recommendation: str
    evidence_ids: list[str] = Field(min_length=1)
class Report(BaseModel):
    summary: str
    findings: list[Finding]
    limitations: list[str] = []
def verify_report(raw, known_ids):
    try: report=Report.model_validate(json.loads(raw))
    except (ValueError,ValidationError) as e: return False,f"Report JSON/schema validation failed: {e}"
    unknown=sorted({x for f in report.findings for x in f.evidence_ids if x not in known_ids})
    if unknown: return False,f"Unknown evidence IDs referenced: {unknown}"
    if not report.findings: return False,"Report contains no evidence-backed findings."
    return True,report.model_dump_json(indent=2)
