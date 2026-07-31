#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CV_PATH = ROOT / "_data" / "cv.yml"
DEFAULT_TEX_PATH = ROOT / "_cv" / "cv.tex"
DEFAULT_PDF_PATH = ROOT / "_cv" / "cv.pdf"
DEFAULT_SITE_PDF_PATH = ROOT / "assets" / "pdf" / "cv.pdf"
DEFAULT_SITE_PREVIEW_PATH = ROOT / "assets" / "img" / "cv-preview.png"


LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
EMPTY_PARENS_RE = re.compile(r"\s*\(\s*\)")
MULTISPACE_RE = re.compile(r"[ \t]{2,}")


def strip_cjk(value: Any) -> str:
    text = str(value).replace("\n", " ").strip()
    text = CJK_RE.sub("", text)
    text = EMPTY_PARENS_RE.sub("", text)
    text = MULTISPACE_RE.sub(" ", text)
    return text.strip()


def tex_escape(value: Any) -> str:
    text = strip_cjk(value)
    return "".join(LATEX_REPLACEMENTS.get(char, char) for char in text)


def tex_url(value: Any) -> str:
    text = str(value).strip()
    return text.replace("%", "%25").replace(" ", "%20").replace("{", "%7B").replace("}", "%7D")


def href(url: Any, label: Any) -> str:
    return rf"\href{{{tex_url(url)}}}{{{tex_escape(label)}}}"


def href_raw(url: Any, raw_label: str) -> str:
    return rf"\href{{{tex_url(url)}}}{{{raw_label}}}"


def entry_title(value: str) -> str:
    return rf"\textcolor{{color1}}{{\bfseries {value}}}"


def education_title(value: str) -> str:
    return rf"{{\small\textcolor{{color1}}{{\bfseries {value}}}}}"


def as_list(value: Any) -> list[Any]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


def format_date(value: Any) -> str:
    text = str(value).strip()
    if text.lower() == "present":
        return "Present"
    return text


def date_range(entry: dict[str, Any]) -> str:
    start = entry.get("start_date") or entry.get("startDate")
    end = entry.get("end_date") or entry.get("endDate")
    if start and end:
        return f"{tex_escape(format_date(start))} -- {tex_escape(format_date(end))}"
    if start:
        return tex_escape(format_date(start))
    if end:
        return tex_escape(format_date(end))
    return ""


def education_date_range(entry: dict[str, Any]) -> str:
    def education_date(value: Any) -> str:
        text = strip_cjk(format_date(value))
        if text.lower() == "present":
            return "Present"
        return tex_escape(text)

    start = entry.get("start_date") or entry.get("startDate")
    end = entry.get("end_date") or entry.get("endDate")
    if start and end:
        return f"{education_date(start)} -- {education_date(end)}"
    if start:
        return education_date(start)
    if end:
        return education_date(end)
    return ""


def join_nonempty(values: list[Any], separator: str = ", ") -> str:
    return separator.join(tex_escape(value) for value in values if value)


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if len(parts) <= 1:
        return full_name.strip(), ""
    return " ".join(parts[:-1]), parts[-1]


def author_name(author: Any) -> str:
    if isinstance(author, dict):
        if author.get("name"):
            return str(author["name"]).strip()
        first = author.get("first") or author.get("given") or ""
        last = author.get("last") or author.get("family") or ""
        return f"{first} {last}".strip()
    return str(author).strip()


def author_line(authors: list[Any], self_name: str) -> str:
    names = [name for name in (author_name(author) for author in authors) if name]
    parts: list[str] = []
    for index, name in enumerate(names):
        if index > 0:
            if index == len(names) - 1 and len(names) == 2:
                parts.append(" and ")
            elif index == len(names) - 1:
                parts.append(", and ")
            else:
                parts.append(", ")

        escaped_name = tex_escape(name)
        if name == self_name:
            parts.append(rf"\textbf{{\underline{{{escaped_name}}}}}")
        else:
            parts.append(escaped_name)
    return "".join(parts)


def itemize(items: list[Any]) -> str:
    filtered_items = [item for item in items if not str(item).strip().lower().startswith("published:")]
    if not filtered_items:
        return ""

    lines = [r"\begin{itemize}"]
    for item in filtered_items:
        lines.append(rf"  \item {tex_escape(item)}")
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def section(title: str) -> list[str]:
    return ["", rf"\section{{{tex_escape(title.upper())}}}"]


def entry_keywords(entry: dict[str, Any]) -> str:
    keywords = entry.get("keywords", "")
    if isinstance(keywords, list):
        return ", ".join(str(keyword) for keyword in keywords)
    return str(keywords)


def is_research_interest(entry: Any) -> bool:
    return isinstance(entry, dict) and str(entry.get("name", "")).strip().lower() == "research"


def education_notes_from_highlights(highlights: list[Any]) -> list[str]:
    notes: list[str] = []
    for highlight in highlights:
        text = strip_cjk(highlight)
        if not text:
            continue
        lower_text = text.lower()
        if lower_text.startswith("published:"):
            continue
        if lower_text.startswith("advisor:") or lower_text.startswith("research focus:"):
            if ":" in text:
                label, value = text.split(":", 1)
                label = label.strip()
                value = value.strip()
                if value:
                    notes.append(rf"\textbf{{{tex_escape(label)}:}} {tex_escape(value)}")
                else:
                    notes.append(rf"\textbf{{{tex_escape(label)}:}}")
            else:
                notes.append(tex_escape(text))
    return notes


def render_header(cv: dict[str, Any]) -> list[str]:
    contact_parts: list[str] = []

    for social in as_list(cv.get("social_networks")):
        if not isinstance(social, dict):
            continue
        network = social.get("network")
        username = social.get("username")
        if network == "GitHub" and username:
            contact_parts.append(rf"\faGithub\enspace {href(f'https://github.com/{username}', f'github.com/{username}')}")
        elif network == "Google Scholar" and username:
            url = social.get("url") or f"https://scholar.google.com/citations?user={username}"
            contact_parts.append(rf"\faGraduationCap\enspace {href(url, 'Google Scholar')}")
        elif network == "ORCID" and username:
            url = social.get("url") or f"https://orcid.org/{username}"
            contact_parts.append(rf"{href(url, 'ORCID')}")
        elif network and username:
            contact_parts.append(tex_escape(f"{network}: {username}"))

    if cv.get("website"):
        contact_parts.append(rf"\faGlobe\enspace {href(cv['website'], cv['website'])}")
    if cv.get("email"):
        email = cv["email"]
        contact_parts.append(rf"\faEnvelope\enspace {href(f'mailto:{email}', email)}")
    if cv.get("phone"):
        contact_parts.append(rf"\faMobile\enspace {tex_escape(cv['phone'])}")
    if cv.get("location"):
        contact_parts.append(rf"\faMapMarker*\enspace {tex_escape(cv['location'])}")

    lines = [
        r"\makecvtitle",
        r"\vspace*{-16mm}",
        r"\begin{center}",
        r"\renewcommand{\arraystretch}{1.3}",
        r"\begin{tabular}{c}",
    ]

    if contact_parts:
        profile_contacts = contact_parts[:3]
        direct_contacts = contact_parts[3:]
        profile_contact_line = r" \quad\textbar\quad ".join(profile_contacts)
        lines.append(rf"{{\small {profile_contact_line}}}\\")
        if direct_contacts:
            direct_contact_line = r" \quad\textbar\quad ".join(direct_contacts)
            lines.append(rf"{{\small {direct_contact_line}}}\\")

    lines.extend(
        [
            r"\end{tabular}",
            r"\end{center}",
            r"\vspace*{-2.5mm}",
        ]
    )

    return lines


def render_education(entries: list[dict[str, Any]]) -> list[str]:
    lines = section("Education")
    for entry in entries:
        institution = rf"- {tex_escape(entry.get('institution', ''))}"
        if entry.get("url"):
            institution = href_raw(entry["url"], institution)

        area = tex_escape(entry.get("area", ""))
        school_line = institution
        if area:
            school_line += rf" {{\normalfont\mdseries\itshape \enspace|\enspace {area}}}"

        left_lines = []
        date = education_date_range(entry)
        if date:
            left_lines.append(rf"{{\bfseries {date}}}")
        if entry.get("studyType"):
            left_lines.append(rf"{{\itshape {tex_escape(entry['studyType'])}}}")
        if entry.get("location"):
            left_lines.append(rf"{{\footnotesize\mbox{{{tex_escape(entry['location'])}}}}}")

        education_notes = education_notes_from_highlights(as_list(entry.get("highlights")))
        right_lines = [education_title(school_line)]
        right_lines.extend(rf"{{\small {note}}}" for note in education_notes)

        lines.extend(
            [
                r"\noindent\begin{tabularx}{\linewidth}{@{}p{0.28\linewidth}@{\hspace{0.9em}}X@{}}",
                r"\begin{minipage}[t]{\linewidth}\raggedright",
                r"\\[-0.05em]".join(left_lines) if left_lines else "~",
                r"\end{minipage} &",
                r"\begin{minipage}[t]{\linewidth}",
                r"\\[-0.12em]".join(right_lines),
                r"\end{minipage}\\",
                r"\end{tabularx}",
            ]
        )
        lines.append(r"\par\vspace{0.75em}")
    return lines


def render_publications(entries: list[dict[str, Any]], self_name: str) -> list[str]:
    lines = section("Publications")
    for entry in entries:
        title = tex_escape(entry.get("title") or entry.get("name") or "")
        if entry.get("url"):
            title += f" {href(entry['url'], '[paper]')}"
        if entry.get("code"):
            title += f" {href(entry['code'], '[code]')}"

        authors = author_line(as_list(entry.get("authors") or entry.get("author")), self_name)
        metadata: list[str] = []
        if entry.get("publisher"):
            metadata.append(rf"\emph{{{tex_escape(entry['publisher'])}}}")
        if entry.get("note"):
            metadata.append(rf"{{\small\itshape {tex_escape(entry['note'])}}}")
        if entry.get("summary"):
            metadata.append(tex_escape(entry["summary"]))

        lines.extend(
            [
                r"\noindent\begin{tabularx}{\linewidth}{@{}Xr@{}}",
                rf"{entry_title(title)} & {{\itshape {tex_escape(entry.get('releaseDate') or entry.get('date') or '')}}}",
                r"\end{tabularx}",
            ]
        )
        if authors:
            lines.append(rf"{{\small {authors}}}\\[-0.15em]")
        for index, detail in enumerate(metadata):
            suffix = r"\\[-0.15em]" if index != len(metadata) - 1 else ""
            lines.append(f"{detail}{suffix}")
        lines.append(r"\par\vspace{0.75em}")
    return lines


def render_skills(entries: list[dict[str, Any]]) -> list[str]:
    lines = section("Skills and Tools")
    lines.append(r"\begin{tabular}{ @{} >{\bfseries}l @{\hspace{6ex}} l }")
    for entry in entries:
        keywords = entry.get("keywords", "")
        if isinstance(keywords, list):
            keywords = ", ".join(str(keyword) for keyword in keywords)
        details = keywords or entry.get("summary") or entry.get("level") or ""
        lines.append(rf"{tex_escape(entry.get('name', ''))}\ & {tex_escape(details)} \\")
    lines.append(r"\end{tabular}")
    return lines


def render_projects(entries: list[dict[str, Any]]) -> list[str]:
    lines = section("Projects")
    for entry in entries:
        name = tex_escape(entry.get("name") or entry.get("title") or "")
        if entry.get("url"):
            name += f" {href(entry['url'], '[code]')}"

        lines.extend(
            [
                r"\noindent\begin{tabularx}{\linewidth}{@{}Xr@{}}",
                rf"{entry_title(name)} & {{\itshape {date_range(entry)}}}",
                r"\end{tabularx}",
            ]
        )
        if entry.get("summary"):
            lines.append(rf"{{\small {tex_escape(entry['summary'])}}}")

        highlights = itemize(as_list(entry.get("highlights")))
        if highlights:
            lines.append(highlights)

        lines.append(r"\par\vspace{0.75em}")
    return lines


def render_named_summary(title: str, entries: list[dict[str, Any]]) -> list[str]:
    lines = section(title)
    lines.append(r"\begin{tabular}{ @{} >{\bfseries}l @{\hspace{6ex}} l }")
    for entry in entries:
        details = entry.get("summary") or entry_keywords(entry) or entry.get("details") or ""
        lines.append(rf"{tex_escape(entry.get('name', ''))}\ & {tex_escape(details)} \\")
    lines.append(r"\end{tabular}")
    return lines


def render_research_interests(entries: list[dict[str, Any]]) -> list[str]:
    research_entries = [entry for entry in entries if is_research_interest(entry)]
    if not research_entries:
        return []

    lines = section("Research Interests")
    interests = [entry_keywords(entry) or entry.get("summary") or entry.get("details") for entry in research_entries]
    lines.append(tex_escape(", ".join(interest for interest in interests if interest)))
    return lines


def render_generic(title: str, entries: list[Any]) -> list[str]:
    lines = section(title)
    for entry in entries:
        if isinstance(entry, str):
            lines.append(rf"\textbullet\ {tex_escape(entry)}\\")
            continue

        if not isinstance(entry, dict):
            lines.append(rf"\textbullet\ {tex_escape(entry)}\\")
            continue

        if entry.get("bullet"):
            lines.append(rf"\textbullet\ {tex_escape(entry['bullet'])}\\")
        elif entry.get("label"):
            lines.append(rf"\textbf{{{tex_escape(entry['label'])}}}: {tex_escape(entry.get('details', ''))}\\")
        else:
            heading = entry.get("title") or entry.get("name") or entry.get("institution") or ""
            detail = entry.get("summary") or entry.get("description") or entry.get("details") or ""
            if heading and detail:
                lines.append(rf"\textbf{{{tex_escape(heading)}}}: {tex_escape(detail)}\\")
            elif heading:
                lines.append(rf"\textbf{{{tex_escape(heading)}}}\\")
            elif detail:
                lines.append(rf"{tex_escape(detail)}\\")
    return lines


def render_sections(cv: dict[str, Any]) -> list[str]:
    self_name = str(cv.get("name", "")).strip()
    sections = cv.get("sections") or {}
    interest_entries = as_list(sections.get("Interests"))
    lines: list[str] = []
    rendered_research_interests = False

    for title, entries in sections.items():
        entries_list = as_list(entries)
        if not entries_list:
            continue

        if title == "Education":
            if not rendered_research_interests:
                lines.extend(render_research_interests(interest_entries))
                rendered_research_interests = True
            lines.extend(render_education(entries_list))
        elif title == "Publications":
            lines.extend(render_publications(entries_list, self_name))
        elif title == "Skills":
            lines.extend(render_skills(entries_list))
        elif title in {"Projects", "Open Source Projects"}:
            lines.extend(render_projects(entries_list))
        elif title == "Interests":
            non_research_entries = [entry for entry in entries_list if not is_research_interest(entry)]
            if non_research_entries:
                lines.extend(render_named_summary(title, non_research_entries))
        elif title == "Languages":
            lines.extend(render_named_summary(title, entries_list))
        else:
            lines.extend(render_generic(title, entries_list))

    return lines


def build_tex(cv: dict[str, Any]) -> str:
    first_name, last_name = split_name(str(cv.get("name", "")))
    lines = [
        r"\documentclass[11pt,a4paper,roman]{moderncv}",
        r"\moderncvstyle{banking}",
        r"\moderncvcolor{blue}",
        r"\nopagenumbers{}",
        r"",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{fontawesome5}",
        r"\usepackage{tabularx}",
        r"\usepackage{ragged2e}",
        r"\usepackage{enumitem}",
        r"\usepackage[scale=0.86]{geometry}",
        r"\usepackage{multicol}",
        r"\usepackage{import}",
        r"\setlist[itemize]{leftmargin=1.2em,noitemsep,topsep=0.15em,parsep=0pt,partopsep=0pt}",
        r"",
        rf"\name{{{tex_escape(first_name)}}}{{{tex_escape(last_name)}}}",
        r"\title{Curriculum Vitae}",
        r"",
        r"\newcommand*{\customcventry}[7][.25em]{",
        r"  \begin{tabular}{@{}l}",
        r"    {\bfseries #4}",
        r"  \end{tabular}",
        r"  \hfill",
        r"  \begin{tabular}{l@{}}",
        r"    {\bfseries #5}",
        r"  \end{tabular} \\",
        r"  \begin{tabular}{@{}l}",
        r"    {\itshape #3}",
        r"  \end{tabular}",
        r"  \hfill",
        r"  \begin{tabular}{l@{}}",
        r"    {\itshape #2}",
        r"  \end{tabular}",
        r"  \ifx&#7&%",
        r"  \else{\\%",
        r"    \begin{minipage}{\maincolumnwidth}%",
        r"      \small#7%",
        r"  \end{minipage}}\fi%",
        r"  \par\addvspace{#1}}",
        r"",
        r"\newcommand*{\customcvproject}[4][.25em]{",
        r"  \begin{tabular}{@{}l}",
        r"    {\bfseries #2}",
        r"  \end{tabular}",
        r"  \hfill",
        r"  \begin{tabular}{l@{}}",
        r"    {\itshape #3}",
        r"  \end{tabular}",
        r"  \ifx&#4&%",
        r"  \else{\\%",
        r"    \begin{minipage}{\maincolumnwidth}%",
        r"      \small#4%",
        r"  \end{minipage}}\fi%",
        r"  \par\addvspace{#1}}",
        r"",
        r"\setlength{\tabcolsep}{12pt}",
        r"\begin{document}",
    ]

    lines.extend(render_header(cv))
    lines.extend(render_sections(cv))
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


def compile_pdf(tex_path: Path, pdf_path: Path) -> None:
    latexmk = shutil.which("latexmk")
    tectonic = shutil.which("tectonic")
    if not latexmk and not tectonic:
        raise RuntimeError("latexmk or tectonic is required to generate the PDF.")

    with tempfile.TemporaryDirectory(prefix="cv-latex-") as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        tmp_tex = tmp_dir / tex_path.name
        shutil.copy2(tex_path, tmp_tex)

        if latexmk:
            command = [
                latexmk,
                "-xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                tmp_tex.name,
            ]
        else:
            command = [tectonic, "--outdir", str(tmp_dir), "--keep-logs", tmp_tex.name]

        result = subprocess.run(
            command,
            cwd=tmp_dir,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError("LaTeX build failed.")

        built_pdf = tmp_dir / tex_path.with_suffix(".pdf").name
        if not built_pdf.exists():
            raise RuntimeError("LaTeX build completed but did not produce a PDF.")

        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built_pdf, pdf_path)


def render_pdf_preview(pdf_path: Path, preview_path: Path) -> None:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        print("warning: pdftoppm not found; skipped CV preview image.")
        return

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    output_prefix = preview_path.with_suffix("")
    result = subprocess.run(
        [
            pdftoppm,
            "-singlefile",
            "-png",
            "-r",
            "180",
            str(pdf_path),
            str(output_prefix),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("CV preview image generation failed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render _data/cv.yml to moderncv LaTeX and PDF.")
    parser.add_argument("--cv", type=Path, default=DEFAULT_CV_PATH, help="Path to the CV YAML file.")
    parser.add_argument("--tex", type=Path, default=DEFAULT_TEX_PATH, help="Output LaTeX path.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF_PATH, help="Output PDF path.")
    parser.add_argument("--site-pdf", type=Path, default=DEFAULT_SITE_PDF_PATH, help="PDF path used by the website.")
    parser.add_argument(
        "--site-preview",
        type=Path,
        default=DEFAULT_SITE_PREVIEW_PATH,
        help="PNG preview path used by the website.",
    )
    parser.add_argument("--no-pdf", action="store_true", help="Only generate LaTeX.")
    args = parser.parse_args()

    with args.cv.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    cv = data.get("cv", data)

    args.tex.parent.mkdir(parents=True, exist_ok=True)
    args.tex.write_text(build_tex(cv), encoding="utf-8")
    print(f"wrote {args.tex}")

    if args.no_pdf:
        return

    compile_pdf(args.tex, args.pdf)
    print(f"wrote {args.pdf}")

    args.site_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.pdf, args.site_pdf)
    print(f"wrote {args.site_pdf}")

    render_pdf_preview(args.site_pdf, args.site_preview)
    print(f"wrote {args.site_preview}")


if __name__ == "__main__":
    main()
