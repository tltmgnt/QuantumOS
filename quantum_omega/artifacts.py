"""Content-addressed local run artifacts and explicit integrity verification."""
from hashlib import sha256
import json
from pathlib import Path


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


class RunArtifacts:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)

    def write(self, name, value):
        if Path(name).name != name or not name.endswith('.json'):
            raise ValueError('Artifact names must be local JSON basenames')
        content = canonical(value)
        with (self.directory/name).open('xb') as output:
            output.write(content)
        return {'path': name, 'sha256': sha256(content).hexdigest(), 'size_bytes': len(content)}

    def finalize(self):
        entries = []
        for path in sorted(self.directory.iterdir()):
            if path.name == 'manifest.json' or not path.is_file() or path.is_symlink():
                raise ValueError('Unexpected run directory contents')
            content = path.read_bytes()
            entries.append({'path': path.name, 'sha256': sha256(content).hexdigest(), 'size_bytes': len(content)})
        self.write('manifest.json', {'schema_version': 1, 'artifacts': entries,
            'trust_model': 'Local checksums only; manifest needs an external trusted anchor to resist coherent rewrites'})


def verify_run(directory):
    from .memory import ScientificMemory
    directory = Path(directory)
    manifest_path = directory/'manifest.json'
    if manifest_path.is_symlink():
        raise ValueError('Symlink manifests are not allowed')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema_version') != 1 or not isinstance(manifest.get('artifacts'), list):
        raise ValueError('Invalid manifest schema')
    seen = set()
    for artifact in manifest['artifacts']:
        name = artifact['path']
        if not isinstance(name, str) or Path(name).name != name or name in seen or name == 'manifest.json':
            raise ValueError('Invalid or duplicate manifest path')
        seen.add(name)
        path = directory/name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Missing artifact or symlink')
        content = path.read_bytes()
        if len(content) != artifact['size_bytes'] or sha256(content).hexdigest() != artifact['sha256']:
            raise ValueError('Artifact integrity check failed: '+name)
    if {p.name for p in directory.iterdir()} != seen | {'manifest.json'}:
        raise ValueError('Unexpected or untracked run files')
    if 'memory.sqlite3' not in seen or 'report.json' not in seen:
        raise ValueError('Incomplete run manifest')
    with ScientificMemory(directory/'memory.sqlite3', read_only=True) as memory:
        memory.verify()
        for source in memory.sources():
            if source.id not in seen or source.locator != 'local:'+source.id:
                raise ValueError('Run source does not resolve to a tracked local artifact')
            if sha256((directory/source.id).read_bytes()).hexdigest() != source.content_sha256:
                raise ValueError('Source provenance fingerprint does not match artifact')
    return {'verified': True, 'artifact_count': len(seen), 'scope': 'Local integrity, not scientific truth'}
