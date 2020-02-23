# Updating Dependencies

To update the python dependencies, the bare minimum packages required is:

    pip install --upgrade pip django\<3.0.0 channels asgiref pillow reportlab django-bootstrap-form pypdf2 aioredis channels-redis

To update postgresql dependencies, add:

    pip install --upgrade psycopg2-binary

And to install django extensions, run:

    pip install --upgrade django-extensions pygraphviz
