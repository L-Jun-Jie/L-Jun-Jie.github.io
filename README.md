# Junjie Li Academic Website

This repository contains the source for Junjie Li's personal academic website:

https://L-Jun-Jie.github.io

The site is a Jekyll-based static website for academic profile, publications,
projects, news, and CV pages.

## Main Content

- Home page: `_pages/about.md`
- Publications: `_bibliography/papers.bib`
- Projects: `_projects/`
- News: `_news/`
- CV page data: `_data/cv.yml`
- LaTeX CV source: `_cv/cv.tex`
- Generated CV PDF: `assets/pdf/cv.pdf`
- Profile image and icons: `assets/img/`

## Local Preview

The recommended local preview method is Docker:

```bash
docker compose up
```

Then open:

```text
http://localhost:8080
```

If dependencies or Docker settings changed, rebuild:

```bash
docker compose up --build
```

## CV PDF

The website CV content is maintained in `_data/cv.yml`. The LaTeX/PDF CV can be
regenerated with:

```bash
python3 bin/render_cv_latex.py
```

This updates `_cv/cv.tex`, `_cv/cv.pdf`, `assets/pdf/cv.pdf`, and the CV preview
image used by the website.

## Deployment

Pushing changes to the main branch triggers the GitHub Pages deployment workflow.
The published site is served from:

```text
https://L-Jun-Jie.github.io
```

