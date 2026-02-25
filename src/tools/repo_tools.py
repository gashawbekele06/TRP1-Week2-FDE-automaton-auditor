import tempfile
import subprocess
import ast
import os
from typing import Dict, Any, List
from langchain_core.tools import tool


@tool
def safe_git_clone(repo_url: str) -> Dict[str, Any]:
    """Clones a git repository to a temporary directory safely."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, tmp_dir],
                check=True, capture_output=True, text=True
            )
            return {"success": True, "path": tmp_dir}
        except subprocess.CalledProcessError as e:
            error = str(e)
            if "authentication" in error.lower():
                return {"success": False, "error": "Git authentication failed"}
            return {"success": False, "error": error}


@tool
def extract_git_history(repo_path: str) -> Dict[str, Any]:
    """Extracts commit history from a local git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--oneline", "--reverse", "--pretty=format:%H %ad %s", "--date=iso"],
            capture_output=True, text=True, check=True
        )
        commits = [line.split(" ", 2) for line in result.stdout.strip().split("\n") if line]
        return {"commits": commits, "count": len(commits)}
    except Exception as e:
        return {"error": str(e)}


@tool
def analyze_graph_structure(repo_path: str) -> Dict[str, Any]:
    """Analyzes a repository for LangGraph StateGraph and fan-out patterns."""
    findings = {"stategraph_found": False, "fanout_detected": False, "files_checked": []}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"): continue
            path = os.path.join(root, file)
            findings["files_checked"].append(path)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if getattr(node.func, "id", "") == "StateGraph":
                            findings["stategraph_found"] = True
                        if isinstance(node.func, ast.Attribute) and node.func.attr == "add_edge":
                            parent = getattr(node, "parent", None)
                            if isinstance(parent, (ast.For, ast.While, ast.ListComp)):
                                findings["fanout_detected"] = True
            except SyntaxError:
                pass
    return findings