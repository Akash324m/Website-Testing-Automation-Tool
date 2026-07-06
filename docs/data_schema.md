# Data Schema

## pages.json

Contains one record per discovered page.

Fields

- id
- url
- title
- description
- screenshot
- template_id
- components
- forms

---

## graph.json

Navigation graph.

Node

- page_id
- state

Edge

- action
- destination

---

## workflows.json

Workflow records.

Fields

- id
- name
- description
- steps
- success_conditions

---

## forms.json

Fields

- id
- page
- inputs
- validations
- submit_button

---

## components.json

Fields

- type
- label
- locator
- role
- confidence

---

## SQLite

Tables

pages

components

forms

workflows

states

edges

templates

embeddings

crawl_history
