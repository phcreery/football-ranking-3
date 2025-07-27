from fastapi.testclient import TestClient

from . import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}


def test_fib_when_n_is_0():
    resp = client.get("/fib?n=0")
    assert resp.status_code == 200
    assert resp.json() == 0


def test_fib_when_n_is_1_and_2():
    resp = client.get("/fib?n=1")
    assert resp.status_code == 200
    assert resp.json() == 1

    resp = client.get("/fib?n=2")
    assert resp.status_code == 200
    assert resp.json() == 1


def test_fib_when_n_larger_than_2():
    resp = client.get("/fib?n=3")
    assert resp.status_code == 200
    assert resp.json() == 2
