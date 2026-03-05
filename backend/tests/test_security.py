import pytest
from utils.password import hash_password, verify_password
from utils.jwt import create_access_token, decode_token

def test_hash_password():
    password = "test123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 50

def test_verify_password():
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False

def test_create_access_token():
    data = {"sub": "1", "role": "user"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_decode_token():
    data = {"sub": "1", "role": "user"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
