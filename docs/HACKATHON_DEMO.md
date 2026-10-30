# ODAR for Nebius x NVIDIA: judge walkthrough

This guide is a concise, reproducible route through the project for reviewers. It distinguishes implemented behavior from provider and deployment evidence that still needs a real run.

## The problem and the idea

Research agents can produce confident answers with weak or circular citations. ODAR makes research actions pass through a separate governance layer: budgets, permissions, cancellation, retrieval safety, evidence evaluation and a final audit are checked outside the controller that proposes the next step. Sources and uncertainty remain visible, and the engine can abstain when support is insufficient.

The hackathon adaptation adds a single-agent adapter for Nebius Token Factory's OpenAI-compatible API and the NVIDIA Nemotron model family. The intended route is a real single-mode research run using Token Factory and an enabled NVIDIA open model. Deep mode is not the Nebius path; it remains Anthropic-only.

## What to inspect

1. Start with the [architecture](ARCHITECTURE.md) to see the controller/governor boundary and evidence flow.
2. Read the [security model and limitations](SECURITY.md), especially that retrieved text is untrusted and the sandbox is process-level, not a VM boundary.
3. Review the adapter implementation in `odar/agent.py` and its deterministic mock coverage in `tests/unit/test_nebius_adapter.py`.
4. Compare the verification approach and reported measurements in [benchmarks](../bench/README.md); the guide there also states the caveats and scorer limitations.
5. Use the screenshots in [`screenshots/`](screenshots/) for the existing product UI. Screenshots are product images, not evidence of a currently hosted demo.

## Reproduce the offline checks

With Python 3.13 and the development dependencies installed as described in the root [README](../README.md#requirements-and-installation):

```bash
python3 -m pytest tests/ -q
python3 -m ruff check odar/ tests/ run_research.py benchmarks/
python3 -m ruff format --check odar/ tests/ run_research.py benchmarks/
python3 -m compileall -q odar run_research.py benchmarks
```

These checks do not call Nebius or prove that a live model request succeeds. CI also defines integration, security, dependency-audit, type-check, container-build and smoke-test jobs; each result should be read from the corresponding run rather than inferred from the workflow file.

## Run the hackathon integration

The following is a real provider call and may consume paid credits. Only run it with an authorized key and a confirmed no-cost balance or explicit spending approval. Never commit the key.

```bash
export NEBIUS_API_KEY='...'
python3 run_research.py run "What are the strongest public sources on [a focused question]?" \
  --model llm --provider nebius --mode single \
  --llm-model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B \
  --timeout 180 --db /tmp/odar-demo.db --output-dir /tmp/odar-demo-output
```

Inspect the generated Markdown and JSON under `/tmp/odar-demo-output/`, plus the job status/events, to confirm which provider, sources, audit result and uncertainty were actually recorded. Redact secrets and private data before sharing run artifacts. A successful call should be described with its observed model and run evidence; do not substitute mock tests for a live result.

## Submission evidence checklist

A credible entry needs all of the following, verified rather than merely documented:

- a successful live run on Nebius Token Factory or AI Cloud using an NVIDIA open model;
- this public, MIT-licensed repository;
- a working demo URL that a reviewer can open;
- a public demonstration video shorter than three minutes;
- the corresponding Devpost entry actually submitted before the deadline.

At the time this guide was prepared, the repository and mocked adapter tests were available, but no live Nebius/NVIDIA run, hosted demo, qualifying public video, or completed Devpost submission had been verified. Do not represent the checklist as complete until each item has evidence. The repository alone is not a submitted hackathon entry.

## Short demo narrative

If recording after the missing evidence is available, show the actual app or CLI rather than slides alone: state the research question; show the selected Nebius/Nemotron configuration; run a narrow question; open the source records and provenance; show how an unsupported or conflicting claim is handled; then show the independent audit and recorded uncertainty. Keep the recording under the event's limit, make it public, and include only a run that actually occurred. Do not claim cost, latency, accuracy or provider success that the captured run does not establish.
