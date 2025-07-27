from .scores import request


def test_request():
    assert request(2021) != None
