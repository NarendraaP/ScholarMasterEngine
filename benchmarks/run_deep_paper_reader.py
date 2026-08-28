import os
import re
import json
import hashlib
from pathlib import Path

REPO_ROOT = Path('/Users/premkumartatapudi/Desktop/ScholarMasterEngine')
PAPERS_DIR = REPO_ROOT / 'docs' / 'papers'
GOVERNANCE_DIR = REPO_ROOT / 'research_governance' / 'final_reviewer_calibrated_portfolio_audit'

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def clean_latex(text):
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r'(?<!\\)%.*$', '', line)
        lines.append(cleaned)
    return chr(10).join(lines)

def parse_manuscript(paper_num):
    filename = f'paper{paper_num}_revised.tex'
    filepath = PAPERS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f'Manuscript not found: {filepath}')
    raw_content = filepath.read_text(encoding='utf-8')
    content = clean_latex(raw_content)
    title_m = re.search(r'\\title(?:\[.*?\])?\{([^}]+)\}', content, re.DOTALL)
    title = title_m.group(1).replace(chr(10), ' ').strip() if title_m else f'Paper {paper_num}'
    title = re.sub(r'\\IEEEauthorrefmark\{.*?\}', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    abstract_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    abstract = abstract_m.group(1).strip() if abstract_m else ''
    abstract_clean = re.sub(r'\s+', ' ', abstract).strip()
    section_matches = list(re.finditer(r'\\section\{([^}]+)\}', content))
    sections = []
    for i, m in enumerate(section_matches):
        sec_title = m.group(1).strip()
        start = m.end()
        end = section_matches[i+1].start() if i+1 < len(section_matches) else len(content)
        sec_body = content[start:end].strip()
        sections.append({
            'title': sec_title,
            'body': sec_body,
            'word_count': len(sec_body.split()),
            'line_count': len(sec_body.splitlines())
        })
    subsections = re.findall(r'\\subsection\{([^}]+)\}', content)
    subsubsections = re.findall(r'\\subsubsection\{([^}]+)\}', content)
    citations = re.findall(r'\\cite\{([^}]+)\}', content)
    all_cited_keys = set()
    for c in citations:
        for k in c.split(','):
            if k.strip():
                all_cited_keys.add(k.strip())
    bibitems = re.findall(r'\\bibitem(?:\[.*?\])?\{([^}]+)\}', raw_content)
    figures = re.findall(r'\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}', content, re.DOTALL)
    tables = re.findall(r'\\begin\{table\*?\}(.*?)\\end\{table\*?\}', content, re.DOTALL)
    equations = re.findall(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', content, re.DOTALL)
    algorithms = re.findall(r'\\begin\{algorithmic\}(.*?)\\end\{algorithmic\}', content, re.DOTALL)
    words = len(content.split())
    lines = len(raw_content.splitlines())
    invariants = re.findall(r'INV-\d+', content)
    return {
        'paper_id': f'P{paper_num}',
        'number': paper_num,
        'title': title,
        'source_path': str(filepath.relative_to(REPO_ROOT)),
        'source_hash': get_file_hash(filepath),
        'raw_length_bytes': len(raw_content.encode('utf-8')),
        'lines': lines,
        'words': words,
        'abstract': abstract_clean,
        'abstract_words': len(abstract_clean.split()),
        'sections': sections,
        'subsections': subsections,
        'subsubsections': subsubsections,
        'citation_count': len(all_cited_keys),
        'cited_keys': sorted(list(all_cited_keys)),
        'bibitem_count': len(bibitems),
        'figure_count': len(figures),
        'table_count': len(tables),
        'equation_count': len(equations),
        'algorithm_count': len(algorithms),
        'invariants_mentioned': sorted(list(set(invariants))),
    }

if __name__ == '__main__':
    papers = {}
    for p in range(1, 26):
        data = parse_manuscript(p)
        papers[f'P{p}'] = data
        print(f"P{p:02d}: {data['title'][:38]}... | Words: {data['words']}, Secs: {len(data['sections'])}, Refs: {data['bibitem_count']}, Figs: {data['figure_count']}, Tabs: {data['table_count']}, Eqns: {data['equation_count']}")
    print('\nSuccessfully loaded all 25 manuscripts!')
