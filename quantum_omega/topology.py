"""Read-only structural analysis; graph reachability is not scientific support."""
from collections import deque
from .core import EpistemicStatus, RelationType

DEPENDENCIES = (RelationType.DEPENDS_ON, RelationType.DERIVED_FROM)


def _graph(claims, relations, kinds):
    if not isinstance(kinds, tuple) or any(not isinstance(k, RelationType) for k in kinds):
        raise ValueError('Relation kinds must be a tuple of RelationType values')
    graph = {c.id: set() for c in claims}
    for relation in relations:
        if relation.source not in graph or relation.target not in graph:
            raise ValueError('Relation references a missing graph endpoint')
        if relation.kind in kinds and relation.status != EpistemicStatus.REJECTED:
            graph[relation.source].add(relation.target)
    return {node: tuple(sorted(targets)) for node, targets in graph.items()}


def shortest_path(claims, relations, source, target, kinds=DEPENDENCIES):
    """Directed unweighted BFS, with lexicographic tie-breaking; None if unreachable."""
    graph = _graph(claims, relations, kinds)
    if source not in graph or target not in graph:
        raise KeyError('Unknown source or target claim')
    parents = {source: None}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        if node == target:
            result = []
            while node is not None:
                result.append(node)
                node = parents[node]
            return tuple(reversed(result))
        for neighbor in graph[node]:
            if neighbor not in parents:
                parents[neighbor] = node
                queue.append(neighbor)
    return None


def _components(graph):
    """Iterative Kosaraju strongly connected components; no recursion depth limit."""
    visited, order = set(), []
    for root in sorted(graph):
        stack = [(root, False)]
        while stack:
            node, finished = stack.pop()
            if finished:
                order.append(node)
            elif node not in visited:
                visited.add(node)
                stack.append((node, True))
                stack.extend((n, False) for n in reversed(graph[node]) if n not in visited)
    reverse = {n: [] for n in graph}
    for node, targets in graph.items():
        for target in targets:
            reverse[target].append(node)
    visited, components = set(), []
    for root in reversed(order):
        if root in visited:
            continue
        stack, component = [root], []
        visited.add(root)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in reverse[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return sorted(components)


def analyze(memory, source=None, target=None):
    """Report structural review prompts without changing any claim or stage."""
    if (source is None) != (target is None):
        raise ValueError('Supply both source and target for path analysis')
    claims, relations = memory.snapshot()
    graph = _graph(claims, relations, DEPENDENCIES)
    incident = {endpoint for r in relations if r.status != EpistemicStatus.REJECTED
                for endpoint in (r.source, r.target)}
    result = {
        'schema_version': 1,
        'interpretation': 'Structural review prompts only; not scientific validation or an explanatory-distance metric.',
        'claim_count': len(claims),
        'relation_count': len(relations),
        'isolated_claims': sorted(c.id for c in claims if c.id not in incident),
        'dependency_cycle_components': [c for c in _components(graph) if len(c) > 1],
        'asserted_contradictions': sorted(r.id for r in relations
            if r.kind == RelationType.CONTRADICTS and r.status != EpistemicStatus.REJECTED),
    }
    if source is not None:
        path = shortest_path(claims, relations, source, target)
        result['dependency_path'] = {
            'source': source, 'target': target, 'claim_ids': path,
            'hop_count': None if path is None else len(path)-1,
        }
    return result


def main():
    import argparse
    import json
    import sqlite3
    from pathlib import Path
    from .memory import ScientificMemory
    parser = argparse.ArgumentParser(description='Analyze structural gaps in local scientific memory')
    parser.add_argument('--database', required=True, type=Path)
    parser.add_argument('--source')
    parser.add_argument('--target')
    args = parser.parse_args()
    if not args.database.is_file():
        parser.exit(2, 'Analysis failed: database must already exist\n')
    try:
        with ScientificMemory(args.database, read_only=True) as memory:
            result = analyze(memory, args.source, args.target)
        print(json.dumps(result, sort_keys=True))
    except (ValueError, KeyError, sqlite3.Error) as error:
        parser.exit(2, f'Analysis failed: {error}\n')


if __name__ == '__main__':
    main()
