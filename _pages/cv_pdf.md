---
layout: page
permalink: /cv/pdf/
title: CV PDF
description:
nav: false
---

{% assign cv_asset_version = site.time | date: "%s" %}
{% assign cv_pdf_url = '/assets/pdf/cv.pdf' | relative_url | append: '?v=' | append: cv_asset_version %}
{% assign cv_preview_url = '/assets/img/cv-preview.png' | relative_url | append: '?v=' | append: cv_asset_version %}

<div class="cv-pdf-preview">
  <a class="cv-pdf-preview-link" href="{{ cv_pdf_url }}" target="_blank" rel="noopener noreferrer">
    <img src="{{ cv_preview_url }}" alt="CV PDF Preview" loading="eager">
  </a>
  <p>
    <a href="{{ cv_pdf_url }}" target="_blank" rel="noopener noreferrer">Open CV PDF</a>
  </p>
</div>
