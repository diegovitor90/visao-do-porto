"""Verificações documentais, sem executar aplicação ou testes funcionais."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fontes', action='store_true', help='Não exigir artefatos renderizados')
    args = parser.parse_args()
    errors = []
    checked = 0
    # Apenas o conjunto desta revisão; links históricos também têm de existir,
    # mas não se reinterpreta o conteúdo dos documentos antigos.
    files = [ROOT / 'README.md', DOCS / 'README.md', DOCS / 'contrato-ia-backend.md']
    for folder in ['arquitetura', 'api', 'operacao']:
        files += [p for p in (DOCS / folder).rglob('*') if p.suffix in {'.md','.adoc','.puml'}]
    files += list((DOCS / 'tools').glob('*.py'))
    for path in files:
        text = path.read_text(encoding='utf-8')
        checked += 1
        if '\ufffd' in text: errors.append(f'UTF-8 inválido: {path}')
        targets = []
        if path.suffix == '.md':
            targets += re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text)
        if path.suffix == '.adoc':
            targets += re.findall(r'(?:include|image)::([^\[]+)\[', text)
        for target in targets:
            if re.match(r'^(?:https?:|mailto:|#)', target): continue
            target = unquote(target.split('#')[0].split(' "')[0])
            if not target: continue
            if path.suffix == '.adoc' and target.endswith(('.svg','.png')):
                resolved = DOCS / 'arquitetura/diagramas/imagens' / target
            else:
                resolved = path.parent / target
            if args.fontes and (resolved.suffix in {'.svg','.png','.html','.pdf'} or '/gerado/' in resolved.as_posix()):
                continue
            if not resolved.exists(): errors.append(f'Link/include inexistente: {path.relative_to(ROOT)} -> {target}')
        if path.suffix == '.puml':
            if not text.startswith('@startuml\n') or not text.rstrip().endswith('@enduml'):
                errors.append(f'Bloco PlantUML inválido: {path}')
            if '!includeurl' in text or re.search(r'!include\s+https?://', text):
                errors.append(f'Include remoto proibido no build: {path}')
        if path.suffix == '.adoc':
            for target in re.findall(r'include::([^\[]+)\[', text):
                if re.match(r'https?://', target) or not (path.parent/target).resolve().is_relative_to(ROOT):
                    errors.append(f'Include fora do repositório: {path}')
    # Contratos de documentação: detectar mudanças que requerem revisão humana.
    source = (ROOT/'backend/fastapi/main.py').read_text(encoding='utf-8')
    ast.parse(source)
    for marker in ['version="0.3.0"', 'MAX_FILE_SIZE = 5 * 1024 * 1024',
                   'MAX_IMAGE_PIXELS = 20_000_000', 'status="COMPLETED"', 'model="yolo11n"']:
        if marker not in source: errors.append('Rever documentação FastAPI: ' + marker)
    props = (ROOT/'backend/backend-springboot/src/main/resources/application.properties').read_text()
    if 'jdbc:h2:mem:visaodoporto' not in props: errors.append('Rever DER e guia: datasource alterado')
    if not args.fontes:
        prov = json.loads((DOCS/'api/gerado/proveniencia.json').read_text(encoding='utf-8'))
        for name, digest in prov['sources_sha256'].items():
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != digest:
                errors.append('Proveniência desatualizada: ' + name)
        for puml in (DOCS/'arquitetura/diagramas/fontes').glob('*.puml'):
            for ext in ['svg','png']:
                output = DOCS/'arquitetura/diagramas/imagens'/f'{puml.stem}.{ext}'
                if not output.exists() or output.stat().st_size < 500:
                    errors.append('Exportação ausente/vazia: ' + str(output))
                elif ext == 'svg':
                    tree = ET.parse(output)
                    if 'Syntax Error' in output.read_text(encoding='utf-8'):
                        errors.append('Erro PlantUML renderizado: ' + str(output))
        html = (DOCS/'arquitetura/gerado/arquitetura.html').read_text(encoding='utf-8')
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        for anchor in re.findall(r'href="#([^"]+)"', html):
            if anchor not in ids: errors.append('Âncora HTML inexistente: ' + anchor)
        if re.search(r'src="https?://', html) or re.search(r'<link[^>]+href="https?://', html):
            errors.append('Recurso de renderização remoto encontrado no HTML')
        pdf = DOCS/'arquitetura/gerado/arquitetura.pdf'
        if not pdf.exists() or pdf.read_bytes()[:5] != b'%PDF-': errors.append('PDF ausente/inválido')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'OK: {checked} fontes verificadas; links/includes, UTF-8 e contratos documentais.'
          + (' Renderizados: SVG/PNG, proveniência, HTML/âncoras e PDF.' if not args.fontes else ' Modo fontes.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
