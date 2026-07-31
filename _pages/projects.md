---
layout: page
title: Projects
description: Research software by Junjie Li for constraint solving, formal methods, and diverse solution sampling.
permalink: /projects/
nav: true
nav_order: 3
page_class: projects-page
---

<p class="projects-intro">Research software for constraint solving, formal methods, and diverse solution sampling.</p>

<div class="project-grid">
  {% assign sorted_projects = site.projects | sort: "importance" %}
  {% for project in sorted_projects %}
    <article class="project-card">
      <div class="project-card-header">
        <span class="project-card-icon" aria-hidden="true">
          <i class="fa-solid {{ project.icon | default: 'fa-code' }}"></i>
        </span>
        <span class="project-card-year">{{ project.year }}</span>
      </div>

      <div class="project-card-content">
        <h2>{{ project.title }}</h2>
        {% if project.description %}
          <p>{{ project.description }}</p>
        {% endif %}

        {% if project.topics %}
          <ul class="project-topics" aria-label="Technologies">
            {% for topic in project.topics %}
              <li>{{ topic }}</li>
            {% endfor %}
          </ul>
        {% endif %}
      </div>

      <div class="project-card-links">
        {% if project.github %}
          <a class="project-primary-link" href="{{ project.github }}" target="_blank" rel="noopener noreferrer">
            <i class="fa-brands fa-github" aria-hidden="true"></i>
            View on GitHub
            <i class="fa-solid fa-arrow-up-right-from-square project-link-arrow" aria-hidden="true"></i>
          </a>
        {% endif %}
        {% if project.paper %}
          <a href="{{ project.paper | relative_url }}">
            <i class="fa-regular fa-file-lines" aria-hidden="true"></i>
            Paper
          </a>
        {% endif %}
      </div>
    </article>

{% endfor %}

</div>
