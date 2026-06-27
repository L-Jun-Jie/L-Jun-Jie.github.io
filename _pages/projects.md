---
layout: page
title: Projects
permalink: /projects/
nav: true
nav_order: 3
---

<div class="project-list">
  {% assign sorted_projects = site.projects | sort: "importance" %}
  {% for project in sorted_projects %}
    <article class="project-list-item">
      <div class="project-list-main">
        <h2>{{ project.title }}</h2>
        {% if project.description %}
          <p>{{ project.description }}</p>
        {% endif %}
      </div>
      <div class="project-list-links">
        {% if project.github %}
          <a href="{{ project.github }}" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-github"></i>
            GitHub
          </a>
        {% endif %}
        {% if project.paper %}
          <a href="{{ project.paper | relative_url }}">Paper</a>
        {% endif %}
      </div>
    </article>
  {% endfor %}
</div>
