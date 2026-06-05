"""Plan consistency checks."""

from __future__ import annotations

from odin_backend.models.task_graph import TaskGraph, TaskNodeStatus


def check_plan_consistency(graph: TaskGraph) -> dict[str, object]:
    issues: list[str] = []
    ids = set(graph.nodes)
    for nid, node in graph.nodes.items():
        for dep in node.dependencies:
            if dep not in ids:
                issues.append(f"task {nid} missing dependency {dep}")
        if node.id in node.dependencies:
            issues.append(f"self-dependency on {nid}")

    if _has_cycle(graph):
        issues.append("dependency cycle detected")

    return {"ok": len(issues) == 0, "issues": issues, "node_count": len(graph.nodes)}


def _has_cycle(graph: TaskGraph) -> bool:
    visited: set[str] = set()
    stack: set[str] = set()

    def visit(nid: str) -> bool:
        if nid in stack:
            return True
        if nid in visited:
            return False
        stack.add(nid)
        visited.add(nid)
        node = graph.nodes.get(nid)
        if node:
            for dep in node.dependencies:
                if visit(dep):
                    return True
        stack.discard(nid)
        return False

    return any(visit(nid) for nid in graph.nodes)
