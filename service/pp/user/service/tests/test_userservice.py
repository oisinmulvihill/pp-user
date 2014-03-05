# -*- coding: utf-8 -*-
"""
Integration Test verifing the client REST interface against the service.

PythonPro Limited

"""
import pkg_resources
import pytest

from pp.auth import pwtools
from pp.user.validate import userdata


def test_secret_for_access_token_recovery_restapi(logger, mongodb, user_svc):
    """Test the REST client's secret token recovery for an access token.
    """
    assert not len(user_svc.api.user.all())
    assert user_svc.api.dump() == []

    username = 'bob'

    access_token = (
        "eyJleHBpcmVzIjogMTAsICJzYWx0IjogImMyNzZjMCIsICJpZGVudGl0eSI6ICJib2Iif"
        "QtSy56A7SfLFayHdmuWdwZDBZESKvDCVAIxwHmYqg1wd8LOn12djG_thZg26TTzknKVqT"
        "GmkOs5hs-B-zSfjVU="
    )

    access_secret = (
        "cf25474cda623fe4cb9cebdbb0c328d44ec33d883d27b8e5dc7d62de2247296fe85e7"
        "3dc6fb2d6cfe19f2c107676b52070010b1f932c6f25f74f308fe19c09f3"
    )

    data = [
        {
            "username": username,
            "tokens": {
                access_token: {
                    "access_secret": access_secret
                }
            },
            "display_name": "Bobby",
            "phone": "12121212",
            "_id": "user-2719963b00964c01b42b5d81c998fd05",
            "email": "bob@example.net",
            "password_hash": pwtools.hash_password('11amcoke')
        },
    ]
    user_svc.api.load(data)

    assert len(user_svc.api.user.all()) == 1

    # Recover the user's secret given the access_token:
    found = user_svc.api.user.secret_for_access_token(access_token)
    assert found == access_secret

    # If the token is unknown the nothing will be returned.
    found = user_svc.api.user.secret_for_access_token('a fake token')
    assert found == None


def test_RestClientPing(logger, mongodb, user_svc):
    """Test the rest client's ping of the user service.
    """
    report = user_svc.api.ping()

    assert report['success'] is True
    report = report['data']

    assert "name" in report
    assert "version" in report
    assert "status" in report

    pkg = pkg_resources.get_distribution("pp-user-service")

    assert report['status'] == 'ok'
    assert report['name'] == 'pp-user-service'
    assert report['version'] == pkg.version


def test_UserLoadingAndDumping(logger, mongodb, user_svc):
    """Test the rest client's ping of the user service.
    """
    assert not len(user_svc.api.user.all())
    assert user_svc.api.dump() == []

    username = u'andrés.bolívar'
    display_name = u'Andrés Plácido Bolívar'
    email = u'andrés.bolívar@example.com'

    data = [
        {
            "username": "bob.sprocket",
            "oauth_tokens": {
                "googleauth": {
                    "request_token": "1234567890"
                }
            },
            "display_name": "Bobby",
            "phone": "12121212",
            "cats": "big",
            "teatime": 1,
            "_id": "user-2719963b00964c01b42b5d81c998fd05",
            "email": "bob@example.net",
            "password_hash": pwtools.hash_password('11amcoke')
        },
        {
            "username": username.encode('utf-8'),
            "display_name": display_name.encode('utf-8'),
            "phone": "",
            "_id": "user-38ed1d2903344702b30bb951916aaf1c",
            "email": email.encode('utf-8'),
            "password_hash": pwtools.hash_password('$admintime$')
        }
    ]

    user_svc.api.load(data)

    assert len(user_svc.api.user.all()) == 2

    item2 = user_svc.api.user.get('bob.sprocket')
    user_dict = data[0]
    assert item2['username'] == user_dict['username']
    assert item2['display_name'] == user_dict['display_name']
    assert item2['email'] == user_dict['email']
    assert item2['phone'] == user_dict['phone']
    assert item2['oauth_tokens'] == user_dict['oauth_tokens']
    assert item2['cats'] == 'big'
    assert item2['teatime'] == 1

    # Test the unicode name as still good:
    item1 = user_svc.api.user.get(username)
    user_dict = data[1]
    assert item1['username'] == username
    assert item1['display_name'] == display_name
    assert item1['email'] == email
    assert item1['phone'] == user_dict['phone']


def test_existing_username(logger, mongodb, user_svc):
    """Test that a username must be unique for created accounts.
    """
    # make sure nothing is there to begin with.
    assert len(user_svc.api.user.all()) == 0

    user = dict(
        username="bob",
        password="123456",
        email="bob.sprocket@example.com",
    )

    bob = user_svc.api.user.add(user)
    assert bob['username'] == 'bob'

    user = dict(
        username="bob",
        password="111111",
        email="fred.bale@example.net",
    )

    with pytest.raises(userdata.UserServiceError):
        user_svc.api.user.add(user)


def test_password_change(logger, mongodb, user_svc):
    """Test changing a user's password.
    """
    username = "bob"
    plain_pw = "123456"

    user = dict(
        username=username,
        password_hash=pwtools.hash_password(plain_pw),
        email="bob.sprocket@example.com",
    )

    user_svc.api.user.add(user)

    result = user_svc.api.user.authenticate(username, plain_pw)
    assert result is True

    # Change and test the old password is no longer valid.
    new_plain_pw = "654321"

    user_svc.api.user.update(dict(
        username=username,
        password_hash=pwtools.hash_password(new_plain_pw),
    ))

    username = user['username']
    assert user_svc.api.user.authenticate(username, plain_pw) is False

    # Now test that password has changed.
    username = user['username']
    assert user_svc.api.user.authenticate(username, new_plain_pw) is True


def test_user_management(logger, mongodb, user_svc):
    """Test the REST based interface to add/remove/update users.
    """
    user = dict(
        username="bob",
        password_hash=pwtools.hash_password("123456"),
        display_name="Bob Sprocket",
        email="bob.sprocket@example.com",
        phone="1234567890",
        #extra={},
    )

    bob = user_svc.api.user.add(user)

    assert bob['username'] == user['username']
    assert bob['display_name'] == user['display_name']
    assert bob['email'] == user['email']
    assert bob['phone'] == user['phone']
    #assert (bob['extra'] == user['extra']

    # Check the unique user id is in the bob dict. Its value is generated
    # by the server.
    assert '_id' in bob

    # No plain text password is stored or sent over the wire:
    assert 'password_hash' in bob

    bob = user_svc.api.user.get(user['username'])

    assert bob['username'] == user['username']
    assert bob['display_name'] == user['display_name']
    assert bob['email'] == user['email']
    assert bob['phone'] == user['phone']
    #assert bob['extra'] == user['extra']
    assert '_id' in bob

    # Check I can't add the same user a second time:
    with pytest.raises(userdata.UserServiceError):
        user_svc.api.user.add(user)

    # Test verifcation of the password:
    plain_pw = "123456"
    username = user['username']
    assert user_svc.api.user.authenticate(username, plain_pw) is True

    plain_pw = "not the correct password"
    username = user['username']
    assert user_svc.api.user.authenticate(username, plain_pw) is False

    # Try updating all user's information that can be changed:
    user = dict(
        username=username,
        password_hash=pwtools.hash_password("654321"),
        display_name="Sprokety Bob",
        email="bob.sprocket@example.com",
        phone="0987654321",
        #extra={"a": 1},
    )

    user_svc.api.user.update(user)

    bob = user_svc.api.user.get(user['username'])

    assert bob['username'] == user['username']
    assert bob['display_name'] == user['display_name']
    assert bob['email'] == user['email']
    assert bob['phone'] == user['phone']
    #assert bob['extra'] == user['extra']

    # Now delete the user's account from the system.
    user_svc.api.user.remove(username)
    with pytest.raises(userdata.UserServiceError):
        user_svc.api.user.remove(username)
