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
NB: You do not have to set the path to `"auth/"`, but what you choose **must** end in a `/`.

## Configuration
`fantastic-goggles` requires the following variables to be set in the environment:
- KEYCLOAK_SERVER: the Keycloak host
- KEYCLOAK_REALM: the realm on the Keycloak host where your client is configured
- KEYCLOAK_CLIENT: the name of the Django app's client on the Keycloak realm
- KEYCLOAK_POST_AUTH_REDIRECT_URI: the URI to redirect to upon successful login using the code grant flow