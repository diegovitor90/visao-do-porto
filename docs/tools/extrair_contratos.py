"""Extrai declarações e OpenAPI sem executar endpoints, YOLO ou testes."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/api/gerado'
JAVA = ROOT / 'backend/backend-springboot/src/main/java/br/com/visaodoporto/backend'


def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')


def extract():
    OUT.mkdir(parents=True, exist_ok=True)
    main = ROOT / 'backend/fastapi/main.py'
    source = main.read_text(encoding='utf-8')
    tree = ast.parse(source)
    snippets = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in {
                'BoundingBox', 'Detection', 'ImageAnalysisResponse'}:
            snippets.append(ast.get_source_segment(source, node))
    assert len(snippets) == 3, 'Rever classes FastAPI: contrato alterado'
    write(OUT / 'fastapi-declaracoes.adoc',
          '// Gerado; editar main.py e regenerar, não este trecho.\n'
          '[source,python]\n----\n' + '\n\n'.join(snippets) + '\n----\n')

    declarations = []
    for filename in ['TrabalhadorRequest.java', 'CapacitacaoRequest.java',
                     'CapacitacaoResponse.java', 'ConsultaCapacitacaoResponse.java']:
        text = (JAVA / 'dto' / filename).read_text(encoding='utf-8')
        # Record sem o helper de mapeamento: tipos e validações originais.
        record = re.search(r'public record .*?\)\s*\{', text, re.S)
        assert record, filename
        declarations.append('[source,java]\n----\n' + record.group(0)[:-1].rstrip() + ' {}\n----\n')
    write(OUT / 'spring-declaracoes.adoc',
          '// Gerado a partir dos records DTO; helpers e imports omitidos.\n' + '\n'.join(declarations))

    # main não importa o detector até uma chamada explícita de _get_detector.
    sys.path.insert(0, str(main.parent))
    import main as vision_main
    assert 'vision_detector' not in sys.modules, 'Detector importado inesperadamente'
    schema = vision_main.app.openapi()
    assert schema['info']['version'] == '0.3.0', 'Rever versão documental'
    assert 'vision_detector' not in sys.modules
    write(OUT / 'openapi-fastapi.json', json.dumps(schema, ensure_ascii=False, indent=2) + '\n')

    sources = [main, ROOT / 'backend/fastapi/vision_detector.py',
               ROOT / 'backend/fastapi/test_main.py',
               ROOT / 'frontend/src/features/analysis/api.ts', ROOT / 'frontend/tests/mvp.spec.ts',
               ROOT / 'frontend/vite.config.ts',
               ROOT / 'backend/backend-springboot/src/main/resources/application.properties']
    for folder in ['entity', 'dto', 'controller', 'service', 'repository', 'config']:
        sources.extend(sorted((JAVA / folder).glob('*.java')))
    sources.extend(sorted((ROOT / 'backend/backend-springboot/src/test').rglob('*.java')))
    provenance = {
        'base_commit_documentado': '65c5f23b3b18f5e7e7e01a5f22c666714914194f',
        'head_local_na_geracao': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'metodo': 'Leitura de fontes; OpenAPI via app.openapi; nenhum endpoint/teste/inferencia executado',
        'sources_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sources},
        'testes_python_encontrados': re.findall(r'^def (test_\w+)\(',
                                              (main.parent / 'test_main.py').read_text(encoding='utf-8'), re.M),
    }
    write(OUT / 'proveniencia.json', json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print(f'Extração documental: {len(sources)} fontes; schema OpenAPI 0.3.0; detector não importado.')


if __name__ == '__main__':
    extract()
