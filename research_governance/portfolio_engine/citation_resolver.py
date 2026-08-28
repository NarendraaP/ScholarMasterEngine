"""
Deterministic Manuscript Citation Resolver for ScholarMaster Research Governance
Parses LaTeX \\cite{} commands and maps keys to \\bibitem{} entries strictly via canonical keys and exact titles.
Prohibits keyword guessing in prose.
"""

import os, re, json, glob

class CitationResolver:
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        else:
            self.root_dir = root_dir
        self.papers_dir = os.path.join(self.root_dir, "docs", "papers")

    def _resolve_key_to_paper_id(self, key, bib_text):
        """
        Deterministic identity resolution via canonical keys and exact bibliographic signatures.
        No keyword substring heuristic guessing.
        """
        k_clean = key.strip()
        
        # 1. Canonical Key Pattern: P01-P25, paper1-paper25, scholar1-scholar25, etc.
        m_canon = re.match(r"^(?:paper|p|scholar)?0*(1[0-9]|2[0-5]|[1-9])$", k_clean, re.IGNORECASE)
        if m_canon:
            return f"P{int(m_canon.group(1)):02d}"

        # 2. Year-prefixed Canonical Keys (e.g. kumar2026scholar22)
        m_year_canon = re.search(r"scholar0*(1[0-9]|2[0-5]|[1-9])$", k_clean, re.IGNORECASE)
        if m_year_canon:
            return f"P{int(m_year_canon.group(1)):02d}"

        # 3. Exact Canonical Series Citation in \bibitem text: "ScholarMaster Series, Paper X"
        m_series = re.search(r"ScholarMaster\s+Series[,\s]+Paper\s+0*(1[0-9]|2[0-5]|[1-9])\b", bib_text, re.IGNORECASE)
        if m_series:
            return f"P{int(m_series.group(1)):02d}"

        return None

    def parse_manuscript_citations(self, paper_number):
        tex_path = os.path.join(self.papers_dir, f"paper{paper_number}_revised.tex")
        if not os.path.exists(tex_path):
            return {"paper": f"P{paper_number:02d}", "citations": [], "bibliography": {}}

        with open(tex_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        content = "".join(lines)

        # 1. Extract \\bibitem entries from thebibliography
        bib_match = re.search(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", content, re.DOTALL)
        bib_entries = {}
        if bib_match:
            raw_bibs = re.findall(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})", bib_match.group(0), re.DOTALL)
            for k, txt in raw_bibs:
                bib_entries[k.strip()] = re.sub(r"\s+", " ", txt).strip()

        # 2. Extract in-text \\cite{...} commands
        cite_pattern = re.compile(r"\\cite(?:p|t|author|year)?\{([^}]+)\}")
        in_text_citations = []
        for line_idx, line in enumerate(lines, start=1):
            for match in cite_pattern.finditer(line):
                for k in match.group(1).split(","):
                    key = k.strip()
                    if key:
                        in_text_citations.append({
                            "key": key,
                            "line_number": line_idx,
                            "raw_command": match.group(0)
                        })

        # 3. Resolve internal paper target
        resolved_citations = []
        for c in in_text_citations:
            k = c["key"]
            bib_text = bib_entries.get(k, "")
            
            target_id = self._resolve_key_to_paper_id(k, bib_text)
            
            resolved_citations.append({
                "citing_paper": f"P{paper_number:02d}",
                "citation_key": k,
                "line_number": c["line_number"],
                "target_paper_id": target_id,
                "citation_type": "ACTUAL_CITATION" if target_id else "EXTERNAL_CITATION",
                "bibliography_entry": bib_text,
                "manuscript_file": os.path.relpath(tex_path, self.root_dir)
            })

        return {
            "paper": f"P{paper_number:02d}",
            "total_in_text_citations": len(in_text_citations),
            "total_bib_entries": len(bib_entries),
            "bibliography": bib_entries,
            "citations": resolved_citations
        }

    def build_actual_citation_graph(self):
        nodes = [f"P{i:02d}" for i in range(1, 26)]
        edges = []
        
        for p in range(1, 26):
            res = self.parse_manuscript_citations(p)
            for cit in res["citations"]:
                if cit["target_paper_id"]: # Only actual internal citations in text
                    edges.append({
                        "citing_paper": cit["citing_paper"],
                        "cited_paper": cit["target_paper_id"],
                        "citation_key": cit["citation_key"],
                        "line_number": cit["line_number"],
                        "manuscript_file": cit["manuscript_file"],
                        "bibliography_entry": cit["bibliography_entry"],
                        "identity_resolution_status": "SOURCE_VERIFIED",
                        "edge_class": "ACTUAL_CITATION"
                    })

        return {
            "graph_type": "ACTUAL_MANUSCRIPT_CITATION_GRAPH",
            "total_nodes": len(nodes),
            "total_actual_internal_edges": len(edges),
            "nodes": nodes,
            "edges": edges
        }

if __name__ == "__main__":
    cr = CitationResolver()
    graph = cr.build_actual_citation_graph()
    print("Actual in-text internal citation edges:", graph["total_actual_internal_edges"])
    for e in graph["edges"]:
        print(f"  {e['citing_paper']} -> {e['cited_paper']} (Key: \\cite{{{e['citation_key']}}} at line {e['line_number']})")
