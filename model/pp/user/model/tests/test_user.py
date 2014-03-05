# -*- coding: utf-8 -*-
"""
Test the MongoDB implementation of user functionality.

"""
import pytest

from pp.auth import pwtools
from pp.user.model import user


def test_user_recovery_for_access_token(logger, mongodb):
    """Test the recover a user's access_secret based on a given access_token.

    """
    assert user.count() == 0
    assert user.dump() == []

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
    user.load(data)

    # Recover the user's secret given the access_token:
    found = user.secret_for_access_token(access_token)
    assert found == access_secret

    # If the token is unknown the nothing will be returned.
    assert user.secret_for_access_token('fake-token') is None


def test_validate_password(logger, mongodb):

    assert user.count() == 0
    assert user.dump() == []

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
    user.load(data)

    assert user.validate_password('bob.sprocket', '11amcoke') is True
    assert user.validate_password('bob.sprocket', 'incorrect') is False
    assert user.validate_password(username, '11amcoke') is False
    assert user.validate_password(username, '$admintime$') is True


def test_dump_and_load(logger, mongodb):
    """Test the dump and loading of the user 'universe'.
    """
    assert user.count() == 0
    assert user.dump() == []

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

    user.load(data)

    assert user.count() == 2

    item2 = user.get('bob.sprocket')
    user_dict = data[0]
    assert item2['username'] == user_dict['username']
    assert item2['display_name'] == user_dict['display_name']
    assert item2['email'] == user_dict['email']
    assert item2['phone'] == user_dict['phone']
    assert item2['oauth_tokens'] == user_dict['oauth_tokens']
    assert item2['cats'] == 'big'
    assert item2['teatime'] == 1

    # Test the unicode name as still good:
    item1 = user.get(username)
    user_dict = data[1]
    assert item1['username'] == username
    assert item1['display_name'] == display_name
    assert item1['email'] == email
    assert item1['phone'] == user_dict['phone']


@pytest.mark.xfail
def test_change_password(logger, mongodb):
    """The the single call to change a users password.
    """
    username = 'bob.sprocket'
    plain_pw = '1234567890'
    confirm_plain_pw = '1234567890'
    new_plain_pw = '0987654321'

    assert user.count() == 0
    assert user.find(username=username) == []

    with pytest.raises(user.UserNotFoundError):
        # The user isn't present to recover
        user.change_password(
            username,
            plain_pw,
            confirm_plain_pw,
            new_plain_pw
        )

    # Add the user:
    user_dict = dict(
        username=username,
        password=plain_pw,
        display_name='Bob Sprocket',
        email='bob.sprocket@example.com',
    )
    item1 = user.add(**user_dict)
    is_valid = pwtools.validate_password(plain_pw, item1['password_hash'])
    assert is_valid is True

    # Now change the password
    user.change_password(
        username,
        plain_pw,
        confirm_plain_pw,
        new_plain_pw
    )

    item2 = user.get(username)

    # old password is not valid:
    is_valid = pwtools.validate_password(plain_pw, item2['password_hash'])
    assert is_valid is False

    is_valid = pwtools.validate_password(
        new_plain_pw, item2['password_hash']
    )
    assert is_valid is True


def testExtraField(logger, mongodb):
    """Test the arbitrary dic that can be used to store useful fields
    per user.
    """
    username = 'bob.sprocket'
    plain_pw = '1234567890'

    assert user.count() == 0
    assert user.find(username=username) == []

    user_dict = dict(
        username=username,
        password=plain_pw,
        display_name='Bob Sprocket',
        email='bob.sprocket@example.com',
        phone='9876543210'
    )
    item1 = user.add(**user_dict)

    # Make sure I cannot add the same username again:
    with pytest.raises(user.UserPresentError):
        user.add(**user_dict)

    assert user.find(username=username) == [item1]
    assert user.has(username) is True
    assert user.count() == 1

    item2 = user.get(username)

    assert item2['username'] == user_dict['username']
    assert item2['display_name'] == user_dict['display_name']
    is_validate = pwtools.validate_password(
        plain_pw, item1['password_hash']
    )
    assert is_validate is True
    is_validate = pwtools.validate_password(
        "not the right one", item1['password_hash']
    )
    assert is_validate is False
    assert item2['email'] == user_dict['email']
    assert item2['phone'] == user_dict['phone']

    # Now update all the user fields that can be changed
    # and add some extra data to the arbitrary fields:
    #
    oauth_tokens = dict(
        # Some pretend googleservice oauth data:
        googleauth=dict(
            request_token="1234567890",
        )
    )

    user_dict = dict(
        username=username,
        # change the password. new_password will be hashed and
        # its has stored as password_hash:
        new_password="ifidexmemwb",
        display_name='Bobby',
        email='bob@example.net',
        phone='12121212',
        oauth_tokens=oauth_tokens,
        cats='big',
        teatime=1,
    )

    user.update(**user_dict)
    item2 = user.get(username)

    assert item2['username'] == user_dict['username']
    assert item2['display_name'] == user_dict['display_name']
    is_validate = pwtools.validate_password(
        "ifidexmemwb", item2['password_hash']
    )
    assert is_validate is True
    is_validate = pwtools.validate_password(
        plain_pw, item2['password_hash']
    )
    assert is_validate is False
    is_validate = pwtools.validate_password(
        "not the right one", item1['password_hash']
    )
    assert is_validate is False
    assert item2['email'] == user_dict['email']
    assert item2['phone'] == user_dict['phone']
    assert item2['oauth_tokens'] == oauth_tokens
    assert item2['cats'] == 'big'
    assert item2['teatime'] == 1


def test_unicode_fields(logger, mongodb):
    """Test the entry of unicode username, email, display name.
    """
    username = u'andrés.bolívar'

    assert user.count() == 0
    assert user.find(username=username) == []

    plain_pw = u'í12345í67890é'

    user_dict = dict(
        username=username,
        password=plain_pw,
        display_name=u'Andrés Plácido Bolívar',
        email=u'andrés.bolívar@example.com',
        phone=u''
    )
    item1 = user.add(**user_dict)

    # Check the password is converted into a hashed password correctly:
    is_validate = pwtools.validate_password(
        plain_pw, item1['password_hash']
    )
    assert is_validate is True

    # Try recoving by username, display_name, etc
    #
    for field in user_dict:
        if field == "password":
            # skip, no such thing as find via password.
            continue

        items = user.find(**{field: user_dict[field]})
        assert items == [item1]
        item1 = items[0]
        assert item1['username'] == user_dict['username']
        assert item1['display_name'] == user_dict['display_name']
        assert item1['email'] == user_dict['email']
        assert item1['phone'] == user_dict['phone']


def testBasicCRUD(logger, mongodb):
    """Test the basic add and get method
    """
    username = 'bob.sprocket'

    assert user.count() == 0

    assert user.find(username=username) == []

    # Test I cannot add a user if I don't provide either a
    # password or a password_hash
    #
    user_dict = dict(
        username=username,
        # Not provied password or password hash
        #password='1234567890',
    )
    with pytest.raises(user.UserAddError):
        user.add(**user_dict)

    plain_pw = '1234567890'

    user_dict = dict(
        username=username,
        password=plain_pw,
        display_name='Bob Sprocket',
        email='bob.sprocket@example.com',
        phone='9876543210'
    )
    item1 = user.add(**user_dict)

    # The password is hashed and then stored as password_hash. The password
    # it removed and never stored.
    assert "password" not in item1

    # Check the password is converted into a hashed password correctly:
    is_validate = pwtools.validate_password(
        plain_pw, item1['password_hash']
    )
    assert is_validate is True

    # Make sure I cannot add the same username again:
    with pytest.raises(user.UserPresentError):
        user.add(**user_dict)

    assert user.find(username=username) == [item1]
    assert user.has(username) is True
    assert user.count() == 1

    item2 = user.get(username)

    assert item2["username"] == user_dict['username']
    assert item2['display_name'] == user_dict['display_name']
    assert item2['email'] == user_dict['email']
    assert item2['phone'] == user_dict['phone']

    user.remove(item2['username'])

    assert user.count() == 0

    assert user.has(item2['username']) is False

    with pytest.raises(user.UserRemoveError):
        user.remove(item2['username'])
