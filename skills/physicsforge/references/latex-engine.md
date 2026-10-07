# PhysicsForge LaTeX Paper Engine

Full instructions for generating compilable research manuscripts.

---

## DOCUMENT CLASS SELECTION

| Paper type | Class |
|---|---|
| Standard full article (default) | `\documentclass[12pt]{article}` |
| Physical Review Letter (≤4 pages) | `\documentclass[aps,prl,reprint,showpacs]{revtex4-2}` |
| JHEP article | `\documentclass[a4paper]{jheppub}` |
| Review paper | `\documentclass[12pt]{article}` with extended bibliography |

---

## STANDARD PREAMBLE (always include)

```latex
\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}

% Mathematics
\usepackage{amsmath, amssymb, amsfonts, amsthm}
\usepackage{mathtools}
\usepackage{physics}
\usepackage{tensor}
\usepackage{slashed}
\usepackage{bbm}
\usepackage{empheq}

% Diagrams
\usepackage{tikz}
\usepackage{tikz-feynman}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

% Tables and figures
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{multirow}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}

% References and links
\usepackage{hyperref}
\usepackage{cleveref}
\usepackage{natbib}
\usepackage{cite}

% Typography
\usepackage{xcolor}
\usepackage{microtype}
\usepackage{authblk}
\usepackage{appendix}
\usepackage{enumitem}

% Custom theorem environments
\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{definition}{Definition}[section]
\newtheorem{postulate}{Postulate}[section]
\newtheorem{conjecture}{Conjecture}[section]
\newtheorem{remark}{Remark}
\theoremstyle{definition}
\newtheorem{example}{Example}[section]

% Custom commands — physics notation
\newcommand{\Lag}{\mathcal{L}}
\newcommand{\Ham}{\mathcal{H}}
\newcommand{\Mink}{\eta_{\mu\nu}}
\newcommand{\lp}{\ell_P}
\newcommand{\Mp}{M_{\text{Pl}}}
\newcommand{\tr}{\mathrm{tr}}
\newcommand{\Tr}{\mathrm{Tr}}
\newcommand{\diag}{\mathrm{diag}}
\newcommand{\sgn}{\mathrm{sgn}}
\newcommand{\hodge}{{\star}}
\newcommand{\Pexp}{\mathcal{P}\exp}
\newcommand{\result}[1]{\begin{empheq}[box=\fbox]{equation}#1\end{empheq}}
\newcommand{\note}[1]{\textcolor{blue}{\textbf{[Note: #1]}}}

% Hyperref setup
\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  citecolor=red,
  urlcolor=teal
}
```

---

## MANDATORY PAPER STRUCTURE

### [1] TITLE BLOCK

```latex
\title{\textbf{Full Descriptive Title:\\
A Subtitle If Needed}}
\author[1]{PhysicsForge Research Engine}
\affil[1]{Frontier Physics Research Division}
\date{\today}
\maketitle
```

### [2] ABSTRACT — 150–250 words, NO citations, NO undefined symbols

Must state:
- (a) the broad problem and why it matters
- (b) the specific gap identified, formally
- (c) the method and mathematical toolkit used
- (d) the key result — state the central equation or finding explicitly
- (e) the novel prediction and its experimental signature

```latex
\begin{abstract}
[150–250 words. Full sentences. Academic register. No placeholders.]
\end{abstract}
```

### [3] KEYWORDS

```latex
\textbf{Keywords:} quantum gravity, spacetime discretization, Planck scale,
renormalization, black hole information paradox, holographic principle
```

### [4] INTRODUCTION — 600–1000 words

Structure:
- **Para 1**: Broad physical context and motivation
- **Para 2**: Statement of the specific problem and why it matters now
- **Para 3**: Survey of prior approaches and why they are insufficient — cite `\cite{}`
- **Para 4**: The specific gap this paper addresses, stated formally and precisely
- **Para 5**: Summary of this paper's approach and main result
- **Para 6**: Roadmap paragraph — "The paper is organized as follows..."

### [5] THEORETICAL BACKGROUND — 500–800 words

- Establish all notation used throughout
- State the existing theoretical framework being extended
- Reproduce key equations from the literature (with citations)
- State conventions: metric signature, units, summation conventions
- Define all tensors, operators, manifolds, fields

```latex
\section{Theoretical Background}
We work in natural units where $\hbar = c = k_B = 1$ throughout,
and adopt the mostly-minus metric signature $(+,-,-,-)$.
The Planck length is $\lp = \sqrt{\hbar G / c^3} \approx 1.616 \times 10^{-35}$ m
and the Planck mass $\Mp = \sqrt{\hbar c / G} \approx 2.176 \times 10^{-8}$ kg.
Einstein summation over repeated indices is assumed.
```

### [6] IDENTIFYING THE GAP — 500–700 words

This section is a **mathematical proof** that a gap exists, not just an assertion.

Show formally WHERE and WHY existing theory fails:
- Divergences that cannot be cured by standard renormalization
- Violated symmetries — show the symmetry explicitly then show it is violated
- Inconsistent limits — show that two valid limits give contradictory results
- Missing terms from symmetry arguments (Ward identities, Noether theorem)
- Anomalies, topology obstructions, or completeness failures

```latex
\section{Identifying the Gap: A Formal Analysis}
\label{sec:gap}

We demonstrate rigorously that the existing framework is incomplete.
Consider the [object/equation]. Under [operation/limit], one finds:
\begin{align}
  \mathcal{X} &= \int_0^\infty \frac{d^4k}{(2\pi)^4}\, \frac{1}{k^2 - m^2}
  \label{eq:divergent-integral}
\end{align}
which diverges as $\Lambda \to \infty$ in a manner that cannot be absorbed
into the existing counterterms because [reason]. Specifically...
```

### [7] NEW FRAMEWORK / DERIVATION — 1500–3000 words

This is the mathematical core. Structure as:

#### 7a. Foundational Postulates
```latex
\subsection{Foundational Postulates}
We build our framework on the following postulates:
\begin{postulate}[Name of Postulate]
\label{post:first}
Statement of postulate in precise mathematical language.
\end{postulate}
```

#### 7b. Construction of the Framework
```latex
\subsection{Construction of the Framework}
Starting from Postulate~\ref{post:first}, we construct the action:
\begin{align}
  S &= \int_{\mathcal{M}} d^4x\, \sqrt{-g}\, \Lag \label{eq:action} \\
    &= \int_{\mathcal{M}} d^4x\, \sqrt{-g}
       \left( \frac{R}{16\pi G} + \Lag_\phi + \Lag_\text{int} \right)
    \label{eq:action-expanded}
\end{align}
where $R$ is the Ricci scalar, $\Lag_\phi$ is the matter Lagrangian
[Eq.~\eqref{eq:matter-lag}], and $\Lag_\text{int}$ is the new interaction
term derived in the following subsection.
```

#### 7c. Boxed Key Results
```latex
\subsection{Key Results}
The central result of this paper is:
\begin{equation}
  \boxed{
    \mathcal{F}_{\mu\nu} = F_{\mu\nu} + \frac{\alpha}{\lp^2}
    \epsilon_{\mu\nu\rho\sigma} \nabla^\rho \Phi^\sigma
  }
  \label{eq:main-result}
\end{equation}
where $\alpha$ is a dimensionless coupling constant determined by
[physical argument], $\lp$ is the Planck length, and $\Phi^\sigma$
is the new vector field introduced in Postulate~\ref{post:second}.
```

#### 7d. Consistency Checks
```latex
\subsection{Consistency Checks}

\paragraph{Dimensional analysis.}
We verify Eq.~\eqref{eq:main-result} is dimensionally consistent.
In natural units, $[\lp] = M^{-1}$, $[\Phi^\sigma] = M^1$,
$[\nabla^\rho] = M^1$, giving $[\alpha/\lp^2 \cdot \nabla\Phi] = M^1 = [F_{\mu\nu}]$. \checkmark

\paragraph{Limiting cases.}
In the limit $\lp \to 0$ (or equivalently $G \to 0$),
Eq.~\eqref{eq:main-result} reduces to $\mathcal{F}_{\mu\nu} = F_{\mu\nu}$,
recovering standard Maxwell electrodynamics~\cite{Jackson1999}. \checkmark

\paragraph{Gauge invariance.}
Under the gauge transformation $A_\mu \to A_\mu + \partial_\mu \chi$,
the new term transforms as... [show explicitly]. \checkmark
```

### [8] PHYSICAL INTERPRETATION — 400–600 words

- What does the mathematics MEAN physically?
- What new physical picture does this framework provide?
- Ontological status of any new entities introduced
- Thought experiments that illuminate the key concepts

### [9] PREDICTIONS & OBSERVATIONAL SIGNATURES — 500–800 words

At least 2–3 concrete, quantitative predictions. For each:
- Derive the observable quantity explicitly
- Give a numerical estimate with current constants
- State which experiment/observatory could test it
- Label as `[NEAR-TERM]`, `[FUTURE]`, or `[IN-PRINCIPLE]`

```latex
\section{Predictions and Observational Signatures}
\label{sec:predictions}

\subsection{Prediction 1: Modified Dispersion Relation}
Our framework predicts a Lorentz-violating correction to the
photon dispersion relation:
\begin{equation}
  \omega^2 = k^2 + \frac{\alpha\, k^4}{\Mp^2}
  \label{eq:dispersion}
\end{equation}
For photons with energy $E \sim 10$ TeV (accessible at the LHC),
this gives a fractional velocity deviation:
\begin{equation}
  \frac{\delta v}{c} \sim \frac{\alpha E^2}{\Mp^2}
  \approx \alpha \times 10^{-28}
\end{equation}
This is within the sensitivity of gamma-ray burst time-delay
measurements by the Fermi-LAT telescope~\cite{FermiLAT2009},
which currently constrains $|\delta v/c| < 10^{-16}$ at $E \sim$ GeV.
[\textbf{FUTURE}: next-generation Cherenkov Telescope Array (CTA)
could probe this at $E \sim 100$ TeV.]
```

### [10] DISCUSSION — 400–700 words

- Broader implications of the framework
- Relationship to other open problems
- What this work does NOT resolve — honest limitations
- Connections to other theoretical frameworks
- New mathematical questions opened

### [11] CONCLUSIONS — 250–400 words

- Restate the gap identified
- Summarize derivation approach
- State key results (repeat boxed equations)
- State main novel prediction
- One paragraph on future directions

### [12] ACKNOWLEDGEMENTS

```latex
\section*{Acknowledgements}
The author thanks the global physics community whose published
work made this synthesis possible, and acknowledges the
open-access repositories arXiv.org and INSPIRE-HEP for
enabling free scientific exchange.
```

### [13] APPENDICES — at least one, minimum 300 words each

```latex
\begin{appendices}

\section{Full Derivation of Equation~\eqref{eq:main-result}}
\label{app:derivation}
[Complete multi-page derivation too long for main text]

\section{Proof of Theorem~\ref{thm:main}}
\label{app:proof}
[Full proof]

\section{Notation and Conventions}
\label{app:notation}
[Complete reference table of all symbols]

\section{Dimensional Analysis Tables}
\label{app:dimensions}
[Full table for every new quantity introduced]

\end{appendices}
```

### [14] BIBLIOGRAPHY — minimum 25 real references

```bibtex
@article{Einstein1915,
  author  = {Einstein, Albert},
  title   = {{Die Feldgleichungen der Gravitation}},
  journal = {Sitzungsberichte der Preussischen Akademie der Wissenschaften},
  year    = {1915},
  pages   = {844--847}
}

@article{Hawking1975,
  author  = {Hawking, S. W.},
  title   = {Particle creation by black holes},
  journal = {Commun. Math. Phys.},
  volume  = {43},
  pages   = {199--220},
  year    = {1975},
  doi     = {10.1007/BF02345020}
}
```

---

## EQUATION ENVIRONMENT STANDARDS

```latex
% Single numbered equation
\begin{equation}\label{eq:name}
  G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}
\end{equation}

% Multi-line derivation with alignment
\begin{align}
  S &= \int d^4x\, \sqrt{-g}\, \Lag \label{eq:S1} \\
    &= \int d^4x\, \sqrt{-g}
       \left(\frac{R}{16\pi G} + \Lag_m\right) \label{eq:S2}
\end{align}

% Boxed central result
\begin{equation}
  \boxed{ E^2 = (pc)^2 + (mc^2)^2 + \delta_{\text{QG}}(E, p) }
\end{equation}

% Cases
\begin{equation}
  \Theta(x) = \begin{cases} 1 & x > 0 \\ 0 & x \leq 0 \end{cases}
\end{equation}
```

---

## TABLE STANDARD

```latex
\begin{table}[h]
\centering
\caption{Dimensional analysis of all new quantities introduced.}
\label{tab:dimensions}
\begin{tabular}{llccc}
  \toprule
  Quantity & Symbol & SI Dimensions & Natural Units & Numerical Value \\
  \midrule
  Planck length & $\lp$ & m & $M_\text{Pl}^{-1}$ & $1.616\times10^{-35}$ m \\
  New coupling  & $\alpha_\star$ & dimensionless & 1 & [derived Sec.~3] \\
  \bottomrule
\end{tabular}
\end{table}
```

---

## FEYNMAN DIAGRAM STANDARD

```latex
\begin{figure}[h]
\centering
\begin{tikzpicture}
\begin{feynman}
  \vertex (a) {\(e^-\)};
  \vertex [right=2cm of a] (b);
  \vertex [above right=2cm of b] (c) {\(e^-\)};
  \vertex [below right=2cm of b] (d) {\(\gamma\)};
  \diagram* {
    (a) -- [fermion] (b) -- [fermion] (c),
    (b) -- [photon] (d),
  };
\end{feynman}
\end{tikzpicture}
\caption{Tree-level QED vertex. The electron (solid line) emits
a photon (wavy line) with amplitude $-ie\gamma^\mu$.}
\label{fig:qed-vertex}
\end{figure}
```

---

## LABEL PREFIX CONVENTIONS

| Prefix | Use for |
|---|---|
| `eq:` | equations |
| `fig:` | figures |
| `tab:` | tables |
| `sec:` | sections |
| `app:` | appendices |
| `thm:` | theorems |
| `lem:` | lemmas |
| `def:` | definitions |
| `post:` | postulates |
| `conj:` | conjectures |

Always use `\cref{}` from cleveref (auto-formats "Eq.", "Fig.", "Theorem", etc.)

---

## PAPER LENGTH CALIBRATION

| User says | Target length | Class |
|---|---|---|
| "short paper" or "letter" | 4–6 compiled pages, ~3000 words | `revtex4-2` prl |
| "full paper" or "article" | 15–30 compiled pages, ~12000 words | `article` or `jheppub` |
| "review paper" | 30–60 pages, ~25000 words | `article` + extended bib |
| (no specification) | Full article, 20+ pages | `article` |

---

## COMPILATION INSTRUCTIONS

Always end the paper output with:

```
Compile with:
  pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex

For tikz-feynman (requires LuaLaTeX):
  lualatex main.tex && bibtex main && lualatex main.tex && lualatex main.tex

Recommended: paste directly into Overleaf.com — all packages pre-installed.
```
