set resources {{resource_type}} {{resource_name}} \
{% if container %}
    --containers={{ container }} \
{% endif %}
{% if limits %}
    --limits={{ limits }} \
{% endif %}
{% if requests %}
    --requests={{ requests }} \
{% endif %}
    --record