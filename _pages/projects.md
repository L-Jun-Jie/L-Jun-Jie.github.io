---
layout: page
title: Projects
permalink: /projects/
nav: true
nav_order: 3
page_class: projects-page
---

<div class="project-list">
  {% assign grouped_projects = site.projects | group_by: "year" | sort: "name" | reverse %}
  {% for year_group in grouped_projects %}
    <section class="project-year-group">
      <h2 class="project-year">{{ year_group.name }}</h2>
      {% assign sorted_projects = year_group.items | sort: "importance" %}
      {% for project in sorted_projects %}
        <article class="project-list-item">
          <div class="project-list-main">
            <h3>{{ project.title }}</h3>
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
    </section>
  {% endfor %}
</div>
