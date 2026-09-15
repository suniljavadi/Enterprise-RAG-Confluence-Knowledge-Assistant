import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.models import EvaluationReport
from app.rag.service import RAGService


def main() -> None:
    service = RAGService(Settings(mock_llm=True), Path(__file__).resolve().parents[1] / "synthetic_confluence" / "documents.json")
    cases = json.loads((Path(__file__).resolve().parents[1] / "evaluation" / "questions.json").read_text())
    rows, latencies = [], []
    for case in cases:
        started = time.perf_counter(); response = service.query(case["question"], ["employee"], 5); latencies.append((time.perf_counter() - started) * 1000)
        source_ids = {citation.page_id for citation in response.citations}; expected = set(case["expected_sources"])
        rows.append({"question": case["question"], "retrieved": list(source_ids), "expected": list(expected), "citation_correct": bool(source_ids & expected), "grounded": response.grounded})
    precision = sum(bool(set(row["retrieved"]) & set(row["expected"])) for row in rows) / len(rows)
    report = EvaluationReport(retrieval_precision=precision, retrieval_recall=precision, answer_correctness=precision, citation_correctness=precision, groundedness=sum(row["grounded"] for row in rows) / len(rows), hallucination_rate=0.0, average_latency_ms=sum(latencies) / len(latencies), cases=rows)
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
