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

## Endpoints
- `GET` `[auth]/auth`: navigate here in the browser to trigger the code grant flow. You will get first redirected to your Keycloak realm's sign-in/register page. Upon successful sign-in/registration, you will be redirected to the page set by `KEYCLOAK_POST_AUTH_REDIRECT_URI` above
- `GET` `[auth]/callback`: **do not** use this directly. It is purely for use for the code grant flow
- `POST` `[auth]/token`: get an access and refresh token to access protected resources
- `POST` `[auth]/refresh`: refresh an access token using the refresh token
- `POST` `[auth]/logout`: log the user out of the current Keycloak session

## Adding OIDC Auth to a DRF view
- Class-based views:
```python
from .serializers import MyModelSerializer
from .models import MyModel
from fantastic_goggles.sync.authentication import OIDCAuthentication


class MyViewSet(ModelViewSet):
    serializer_class = MyModelSerializer
    queryset = MyModel.objects.all()
    authentication_classes = [OIDCAuthentication]
```

- Function-based views
```python
from rest_framework.decorators import api_view, authentication_classes
from fantastic_goggles.sync.authentication import OIDCAuthentication
from .serializers import MyModelSerializer
from .models import MyModel


@api_view(["GET"])
@authentication_classes([OIDCAuthentication])
def test_something(request: Request) -> Response:
    my_models = MyModel.objects.all()
    serializer = MyModelSerializer(my_models)
    return Response(
        data=serializer.data,
        status=status.HTTP_200_OK,
    )
```