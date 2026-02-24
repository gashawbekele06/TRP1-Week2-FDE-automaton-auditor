# The Automaton Auditor
FDE Challenge Week 2: Orchestrating Deep LangGraph Swarms for Autonomous Governance

The Automaton Auditor is a Deep LangGraph Swarm designed to autonomously governance code repositories using Dialectical Synthesis. It utilizes isolated Detectives (for repo AST reading and PDF parsing) paired with adversarial Judges (Prosecutor, Defense, TechLead) to apply nuanced rubrics. Finally, a Chief Justice Node deterministically resolves conflict and issues a comprehensive Markdown Audit Report.

## Architecture

This project strictly adheres to the "Digital Courtroom" design:
- **Layer 1: Detectives** (`RepoInvestigator`, `DocAnalyst`, `VisionInspector`) execute Forensics by collecting parsed evidence (AST graphs, Docling parsed chunks, tempfile sandboxed Git History).
- **Layer 2: Synrchonization** (`EvidenceAggregator`) enforces a Fan-In state synchronization before judging.
- **Layer 3: Judges** (`Prosecutor`, `Defense`, `TechLead`) run in parallel via Fan-Out, applying their unique personas to unstructured LLM prompts bounded by `with_structured_output` validation.
- **Layer 4: Chief Justice** resolves multi-agent conflict using strict Rules of Security, Fact Supremacy, and Function Weight. Outputting an actionable, aggregated audit.

## Setup Instructions

This project uses `uv` for minimal, lightning-fast dependency management.

1. Ensure `uv` is installed globally.
2. Initialize environment:
```bash
uv sync
```
3. Setup Environment Variables:
```bash
cp .env.example .env
# Edit .env and supply your OpenAI and LangSmith keys.
```

## Running the Swarm

The entry point for the swarm is `src/graph.py` which requires a target `--repo` and target `--pdf`.

```bash
uv run python src/graph.py --repo "https://github.com/my/target-auditor" --pdf "reports/my_report.pdf" --output "audit/report_onself_generated.md"
```

## Traceability
Set `LANGCHAIN_TRACING_V2=true` in your `.env`. Due to the high degree of Fan-Out/Fan-In parallelism, debugging requires Langsmith traces to verify evidence payload reduction correctly handles state.
