kubectl -n {{ namespace }} get {{ resource_type }} {% if resource_name %} {{ resource_name }} {% endif %} -o json