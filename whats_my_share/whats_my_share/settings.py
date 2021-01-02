from .default_settings import * # noqa

DATABASES["default"]["NAME"] = os.getenv("DATABASE_NAME", "shared_expenses")
DATABASES["default"]["USER"] = os.getenv("DATABASE_USER", "admin")
DATABASES["default"]["PASSWORD"] = os.getenv("DATABASE_PASSWORD", "1.#fampay@321")
DATABASES["default"]["HOST"] = os.getenv("DATABASE_HOST", "localhost")
DATABASES["default"]["PORT"] = os.getenv("DATABASE_PORT", 5432)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", True)

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ['*'])
