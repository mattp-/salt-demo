{% set tgt = pillar['tgt'] %}
{% set pkg = pillar['pkg'] %}

{{ tgt }}-install-{{ pkg }}:
  salt.state:
    - tgt: {{ tgt }}
    - sls: pkg.{{ pkg }}
    - pillar: {{ pillar | yaml }}
