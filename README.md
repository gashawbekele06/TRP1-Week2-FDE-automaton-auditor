# The Automaton Auditor (Interim Submission)
FDE Challenge Week 2: Orchestrating Deep LangGraph Swarms for Autonomous Governance

The Automaton Auditor is a Deep LangGraph Swarm designed to autonomously governance code repositories. 

This repository reflects the **Interim Phase**, containing the Detective Layer. It utilizes isolated Detectives (`RepoInvestigator`, `DocAnalyst`, and `VisionInspector`) running in a Fan-Out pattern, parsing GitHub Repositories (AST verification, git log analysis) and PDF documentation. It extracts structured Pydantic `Evidence` objects and aggregates them via a central Fan-In node (`EvidenceAggregator`).

## Architecture (Interim)

- **Layer 1: Detectives** execute Forensics by collecting parsed evidence:
  - `RepoInvestigator`: Clones the repo to a sandboxed `tempfile` and uses Python `ast` to verify `StateGraph` usage and typed reducers.
  - `DocAnalyst`: Uses `docling` to chunk and semantically review PDF files.
  - `VisionInspector`: Extensible node for diagram analysis.
- **Layer 2: Synchronization** (`EvidenceAggregator`) enforces a Fan-In state synchronization, outputting the gathered proof locally.
- *(Judges and ChiefJustice logic reserved for Final Submission).*

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

The interim graph requires a target `--repo` and target `--pdf`.

```bash
uv run python src/graph.py --repo "https://github.com/langchain-ai/langchain" --pdf "reports/interim_report.pdf"
```
