"""Run NIST's three probes, unchanged, over a report section citing three
documents that descend from one observation.

Why not the whole pipeline: NIST's report generator sends `reasoning_effort`
(exhaustive_scanner.py:104, pipeline.py:115) alongside `temperature`. OpenAI's
reasoning models reject a non-default temperature and its chat models reject
reasoning_effort, so the generator cannot run against the public API without
editing NIST's code. The probes are different: `probes/_judge.py::call_judge`
sends only model, messages, temperature and response_format. They run unchanged.

So the section is written by gpt-4.1 from the three documents, and then NIST's
faithfulness, completeness and sufficiency probes grade it. What is under test
is the probes, and they are untouched.

To reproduce:

    git clone https://github.com/usnistgov/agentic-research-evaluation-probes
    cd agentic-research-evaluation-probes
    pip install -r requirements.txt
    cp -r /path/to/this/directory/corpus ./crossing-corpus
    cp /path/to/this/directory/run_probes.py .
    OPENAI_API_KEY=... CROSSING_CORPUS=./crossing-corpus python3 run_probes.py

Check `num_parse_error` in the output before reading any mean score. The probes
issue their judge calls concurrently and a token-per-minute limit turns verdicts
into PARSE_ERROR scored 0.0, which is indistinguishable from disagreement in the
mean alone.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(Path.home() / ".config" / "odr.env")

MODEL = os.environ.get("ODR_JUDGE_MODEL", "gpt-4.1")
# Defaults to the corpus beside this file. Override with CROSSING_CORPUS when the
# script is copied into a NIST checkout, as the run instructions describe.
CORPUS = Path(os.environ.get("CROSSING_CORPUS",
                             Path(__file__).resolve().parent / "corpus"))
QUESTION = ("What thermal drift has been reported for Kestrel-7 sensor arrays "
            "under extended hold at elevated temperature, and what is the "
            "evidence for it?")


async def write_section(client, docs) -> str:
    listing = "\n\n".join(
        f"[Source {i}] {name}\n{text}" for i, (name, text) in enumerate(docs, 1))
    prompt = (
        f"Write one section of a research report answering this question:\n\n"
        f"{QUESTION}\n\n"
        f"Use footnote citations in the form [^N] where N is the source number. "
        f"Cite every source you rely on. Be accurate and do not overstate. "
        f"Write 4-6 sentences.\n\n{listing}"
    )
    r = await client.chat.completions.create(
        model=MODEL, temperature=0.2,
        messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content.strip()


async def main() -> None:
    from models import Finding, SectionResult
    from citations.tracker import CitationTracker
    from probes import run_probes
    from research.context import ResearchContext, ResearchInfrastructure, ResearchState
    from store.document_store import DocumentStore

    docs = [(p.name, p.read_text()) for p in sorted(CORPUS.glob("*.md"))]
    assert len(docs) == 3, docs
    client = AsyncOpenAI()

    content = await write_section(client, docs)
    print("=== SECTION AS WRITTEN ===\n")
    print(content)
    print()

    findings = [
        Finding(citation_id=i, chunk_id=f"chunk-{i}", source_file=name,
                heading="", text=text)
        for i, (name, text) in enumerate(docs, 1)
    ]
    section = SectionResult(section_title="Reported thermal drift",
                            content=content, citations_used=[1, 2, 3], order=1)

    infra = ResearchInfrastructure(
        document_store=DocumentStore(CORPUS),
        citation_tracker=CitationTracker(),
        openai_client=client,
        model_name=MODEL,
    )
    context = ResearchContext(infra=infra,
                              state=ResearchState(research_question=QUESTION))

    # Your org's TPM limit for this model is 30k. NIST's dispatcher fires every
    # probe's judge calls concurrently, which exceeds it and turns verdicts into
    # PARSE_ERROR (HTTP 429). The probes are NOT modified: they are simply
    # invoked one at a time with a pause, so each stays inside the window.
    from probes import _PROBE_REGISTRY
    for i, probe_fn in enumerate(_PROBE_REGISTRY):
        if i:
            print(f"   ... pausing 70s to stay under the token-per-minute limit")
            await asyncio.sleep(70)
        print(f"running {probe_fn.__name__}")
        result = await probe_fn(section, findings, context)
        # The dispatcher normally stores this; we are calling the probes
        # directly, so store it the same way it would.
        key = getattr(result, "probe_name", None) or probe_fn.__name__
        section.probe_results[key] = result

    print("=== PROBE RESULTS (NIST code, unchanged) ===")
    out = {"model": MODEL, "question": QUESTION, "section": content, "probes": []}
    def field(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    for name, probe in section.probe_results.items():
        mean = field(probe, "mean_score")
        summary = field(probe, "summary")
        entry = {"probe": name, "mean_score": mean,
                 "summary": summary, "verdicts": []}
        print(f"\n{name}: mean_score = {mean}   {summary}")
        for v in field(probe, "verdicts", []) or []:
            vd = field(v, "verdict")
            sc = field(v, "score")
            cid = field(v, "citation_id")
            print(f"   citation [^{cid}] -> {vd} ({sc})")
            entry["verdicts"].append({
                "citation_id": cid, "verdict": vd, "score": sc,
                "rationale": (field(v, "rationale", "") or "")[:400]})
        out["probes"].append(entry)

    Path("probe-results.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print("\nwritten: probe-results.json")


if __name__ == "__main__":
    asyncio.run(main())
