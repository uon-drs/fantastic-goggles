# Fantastic Goggles
A package showing how you might use Django + DRF with Keycloak.

## Installation
- Using pip:
```bash
pip install git+https://github.com/uon-drs/fantastic-goggles.git
```

- Add to `pyproject.toml` (Poetry example)
```toml
[tool.poetry.dependencies]
...
fantastic-goggles = { git = "https://github.com/uon-drs/fantastic-goggles.git" }
...
```

## Add to Django app
- `settings.py`
```python
INSTALLED_APPS = [
    ...
    # if using a synchronous server
    "fantastic_goggles.sync"
    # if using an asynchronous server
    "fantastic_goggles.async"
    ...
]
```
- in the main `urls.py`
```python
urlpatterns = [
    ...
    # if using a synchronous server
    path("auth/", include("fantastic_goggles.sync.urls")),
    # if using an asynchronous server
    path("auth/", include("fantastic_goggles.async.urls")),
    ...
]
```