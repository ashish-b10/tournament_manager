from pathlib import Path

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(Path(__file__).parent.parent.parent / 'tmdb.sqlite3'),
    }
}

REDIS_HOST = 'localhost'
