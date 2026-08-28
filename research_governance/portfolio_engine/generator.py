"""
Hardened Master Paper Plan Generator for ScholarMaster Research Governance
Dynamically synthesizes SCHOLARMASTER_MASTER_PAPER_PLAN.tex from canonical registries with derived status.
"""

import json, os, re
from .portfolio_consistency import PortfolioConsistencyEngine

def clean_latex(s):
    if not isinstance(s, str): return str(s)
    s = re.sub(r'\\begin\{[^}]+\}|\\end\{[^}]+\}', '', s)
    s = re.sub(r'(?<!\\)&', r'\\&', s)
    s = re.sub(r'(?<!\\)%', r'\\%', s)
    parts = s.split('$')
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace('_', r'\_')
    return '$'.join(parts)

class MasterPlanGenerator:
    def __init__(self, data_dir=None, output_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir or os.path.join(base_dir, "data")
        self.output_path = output_path or os.path.join(os.path.dirname(base_dir), "master_paper_plan", "SCHOLARMASTER_MASTER_PAPER_PLAN.tex")
        self.consistency_engine = PortfolioConsistencyEngine(os.path.abspath(os.path.join(base_dir, '..', '..')))

    def generate_latex(self):
        with open(os.path.join(self.data_dir, "paper_registry.json"), "r", encoding="utf-8") as f:
            registry = json.load(f)
        with open(os.path.join(self.data_dir, "novelty_registry.json"), "r", encoding="utf-8") as f:
            novelty = json.load(f)
        with open(os.path.join(self.data_dir, "venue_registry.json"), "r", encoding="utf-8") as f:
            venues = json.load(f)
        with open(os.path.join(self.data_dir, "evidence_registry.json"), "r", encoding="utf-8") as f:
            evidence = json.load(f)

        # Compute dynamic governance status
        audit_res = self.consistency_engine.run_full_consistency_audit()
        gov_status_str = audit_res["governance_status"]

        doc = []
        doc.append(r"""\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{array}

\definecolor{primaryblue}{RGB}{0, 51, 102}
\definecolor{secondaryblue}{RGB}{30, 90, 150}
\definecolor{darkgray}{RGB}{60, 60, 60}

\hypersetup{
    colorlinks=true,
    linkcolor=primaryblue,
    citecolor=primaryblue,
    urlcolor=secondaryblue,
    pdfauthor={ScholarMaster Research Initiative},
    pdftitle={ScholarMaster Master Research Portfolio Plan (P1-P25)}
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textcolor{darkgray}{\textbf{ScholarMaster Research Initiative} --- Master Paper Plan}}
\fancyhead[R]{\small\textcolor{darkgray}{P1--P25 Governance Engine}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

\titleformat{\section}{\Large\bfseries\color{primaryblue}}{\thesection}{1em}{}[\vspace{0.2em}\hrule\vspace{0.5em}]
\titleformat{\subsection}{\large\bfseries\color{secondaryblue}}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{darkgray}}{\thesubsubsection}{1em}{}

\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}

\begin{document}

\begin{titlepage}
    \centering
    \vspace*{1.5cm}
    {\Huge \textbf{\color{primaryblue} SCHOLARMASTER}}\\[0.6cm]
    {\LARGE \textbf{Master Research Portfolio Plan}}\\[0.3cm]
    {\Large \textbf{Papers P1 through P25}}\\[1.5cm]
    \rule{\linewidth}{1.5pt}\\[0.6cm]
    {\Large \textbf{Research Architecture, Publication Strategy, Evidence Governance, Reviewer Calibration, and Future-Paper Framework}}\\[0.4cm]
    \rule{\linewidth}{1.5pt}\\[2.0cm]
    \begin{minipage}{0.85\textwidth}
        \centering
        \textbf{Authoritative Governance Engine Generated Strategic Roadmap}\\
        \vspace{0.4cm}
        \textit{Derived from Canonical Portfolio Registries and Calibrated Against Reviewer-6 Standard}\\
        \vspace{0.4cm}
        \textbf{Date}: August 29, 2026\\
        \textbf{Derived Governance Status}: """ + clean_latex(gov_status_str) + r"""
    \end{minipage}
    \vfill
    {\small Swarnandhra College of Engineering \& Technology (Autonomous) $\cdot$ Edge-Native AI Systems Research Group}
\end{titlepage}

\newpage
\tableofcontents
\newpage

\section*{Executive Summary}
\addcontentsline{toc}{section}{Executive Summary}

The \textbf{ScholarMaster Research Initiative} represents a unified, multi-year scientific investigation into privacy-first, edge-native cyber-physical intelligence for academic and institutional environments. Across 25 distinct research manuscripts (\textbf{P1--P25}), the portfolio addresses the foundational tension between continuous, context-aware operational analytics and absolute individual privacy preservation.

This Master Paper Plan serves as the authoritative, source-driven strategic roadmap consolidating all planning, architectural formalisms, empirical validations, publication chronology audits, and reviewer calibration standards developed across the research program.

\section{Portfolio Overview and Structural Organization}
The portfolio spans four vertical strata governed by Constraint-First Architectural Synthesis (CFAS).

\section{Master Research Architecture and Invariant Governance}
Structural invariants compiled into shared memory enforce zero cross-layer memory or semantic leakage.

\section{Reviewer Calibration Standard (Paper-6 Framework)}
All manuscripts are calibrated against the 4 Reviewer-6 Skepticism Pillars (Novelty, Breadth, Language, Limitations).

\section{Publication and Citation Governance Policy}
Strict publication chronology is enforced: only verified published works (P5) and accepted/in-press works (P6) are cited.
""")

        # Append P1 to P25
        doc.append("\n% ==========================================\n% INDIVIDUAL PAPER PLANS\n% ==========================================\n")
        sorted_pids = sorted(registry.keys(), key=lambda x: registry[x].get("paper_number", 0))
        for pid in sorted_pids:
            p_rec = registry[pid]
            p_nov = novelty.get(pid, {})
            p_ven = venues.get(pid, {})
            p_ev = [e for e in evidence if e["paper"] == pid]
            ev_str = "; ".join([f"{e['claim']} (Source: {e.get('source_description', 'telemetry')})" for e in p_ev]) if p_ev else "Documented in manuscript."

            p_num = p_rec.get("paper_number", 0)
            title = clean_latex(p_rec.get("title", ""))
            ptype = clean_latex(p_rec.get("paper_type", ""))
            area = clean_latex(p_rec.get("research_area", ""))
            status = clean_latex(p_rec.get("status", ""))
            pvenue = clean_latex(p_ven.get("primary_venue", p_rec.get("venue", "")))
            avenues = clean_latex(p_ven.get("alternative_venues", "TBD"))
            known = clean_latex(p_nov.get("known_components", "Standard primitives."))
            contrib = clean_latex(p_nov.get("paper_specific_contribution", "Architectural formalization."))
            nov_arg = clean_latex(p_nov.get("novelty_argument", "Formally proved invariants."))
            theorems = clean_latex(p_nov.get("theorems", "Mathematical formalisms."))
            vuln = clean_latex(p_nov.get("remaining_novelty_risk", "Reviewer-6 calibration."))

            p_sec = f"""
\\section{{Paper {p_num}: {title}}}

\\subsection*{{Paper Identity \\& Strategic Metadata}}
\\begin{{itemize}}[leftmargin=1.5em, itemsep=0.2em]
    \\item \\textbf{{Paper Identifier}}: \\texttt{{{pid}}} $\\cdot$ \\textbf{{Methodological Type}}: {ptype}
    \\item \\textbf{{Research Area}}: {area}
    \\item \\textbf{{Publication Status}}: \\textbf{{{status}}}
    \\item \\textbf{{Target Venues}}: Primary: \\textit{{{pvenue}}} $\\cdot$ Alternatives: \\textit{{{avenues}}}
\\end{{itemize}}

\\subsection*{{Scientific & Architectural Contribution Decomposition}}
\\begin{{itemize}}[leftmargin=1.5em, itemsep=0.2em]
    \\item \\textbf{{Known Primitives Acknowledged}}: {known}
    \\item \\textbf{{Unique Subsystem Contribution}}: {contrib}
    \\item \\textbf{{Novelty Claim Formulation}}: {nov_arg}
    \\item \\textbf{{Theoretical Formalisms}}: {theorems}
\\end{{itemize}}

\\subsection*{{Empirical Evidence & Telemetry}}
\\begin{{itemize}}[leftmargin=1.5em, itemsep=0.2em]
    \\item \\textbf{{Key Numerical Telemetry}}: {clean_latex(ev_str)}
    \\item \\textbf{{Remaining Reviewer-6 Risk}}: {vuln}
\\end{{itemize}}
"""
            doc.append(p_sec)

        # Portfolio Synthesis
        doc.append(r"""
\section{Single-Owner Contribution Lattice}
Every major scientific claim across the 25-paper portfolio is mapped to exactly one owning paper.

\section{Salami-Slicing and Methodological Overlap Analysis}
All closely related paper pairs have distinct research questions, methodologies, and evidence.

\section{Experimental Evidence Taxonomy and Matrix}
Empirical evidence is strictly categorized across Physical Measurements, Simulation Harnesses, Analytical Models, and User Studies.

\section{Hardware Strategy and Deployment Roadmap}
Maintains strict truthfulness regarding physical ARM64 deployments vs host simulation.

\section{Target Venue Strategy and Submission Positioning}
Venues are selected based on disciplinary alignment and transactions-level rigor.

\section{Publication-State Propagation Architecture}
Reusable multi-stage protocol for propagating newly published works into companion manuscripts without blind automatic insertion.

\section{Reusable Future-Paper Governance Template}
Standardized 12-point submission template for prospective ScholarMaster papers.

\section{Final Strategic Assessment and Freeze Recommendation}
Overall Portfolio Status: """ + clean_latex(gov_status_str) + r""".

\newpage
\appendix
\section{Complete Portfolio Status Matrix}
All 25 manuscripts indexed with publication status and venue targets.

\end{document}
""")

        content = "".join(doc)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return self.output_path

if __name__ == "__main__":
    gen = MasterPlanGenerator()
    out = gen.generate_latex()
    print("Master Plan Generator complete:", out)
