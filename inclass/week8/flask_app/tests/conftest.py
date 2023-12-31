import pytest
from mongoengine.connection import disconnect

from types import SimpleNamespace

from flask_app import create_app, bcrypt
from flask_app.models import User, Post
from flask_app.forms import LoginForm, RegistrationForm

TEST_MONGODB_HOST = 'mongodb+srv://cmsc388j:<password>@cluster0.23mylkm.mongodb.net/week8_db_test?retryWrites=true&w=majority'

@pytest.fixture
def app(request):
    test_config = {
        "TESTING": True,
        "MONGODB_HOST": TEST_MONGODB_HOST,
        "WTF_CSRF_ENABLED": False,
    }
    disconnect()
    app = create_app(test_config)

    User.drop_collection()
    Post.drop_collection()

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def client(app):
    """ Creates a test client """
    return app.test_client()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def register(
        self, username="test", email="test@test.com", passwrd="test", confirm="test"
    ):
        registration = SimpleNamespace(
            username=username,
            email=email,
            password=passwrd,
            confirm_password=confirm,
            submit="Sign Up",
        )
        form = RegistrationForm(formdata=None, obj=registration)
        response = self._client.post("/register", data=form.data, follow_redirects=True)

        return response

    def login(self, username="test", password="test"):
        login = SimpleNamespace(
            username=username,
            password=password,
            submit="Login",
        )

        form = LoginForm(formdata=None, obj=login)
        response = self._client.post("/login", data=form.data, follow_redirects=True)
        return response

    def logout(self):
        return self._client.get("/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
