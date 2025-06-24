import pytest
from atm import app, users

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    with app.test_client() as client:
        with app.app_context():
            yield client

def login(client, accno, pin):
    return client.post('/', data={'accno': accno, 'pin': pin}, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_valid_login(client):
    response = login(client, 1001, 1111)
    assert b"Welcome" in response.data or b"Menu" in response.data

def test_invalid_login_wrong_pin(client):
    response = login(client, 1001, 1234)
    assert b"Incorrect PIN" in response.data

def test_invalid_login_nonexistent_account(client):
    response = login(client, 9999, 1111)
    assert b"Account number does not exist" in response.data

def test_view_balance(client):
    login(client, 1002, 2222)
    response = client.get('/balance')
    assert b"15000" in response.data

def test_deposit_valid_amount(client):
    login(client, 1003, 3333)
    original = users[1003]['amount']
    response = client.post('/deposit', data={'amount': 5000}, follow_redirects=True)
    assert users[1003]['amount'] == original + 5000
    assert b"25000" in response.data

def test_deposit_invalid_amount(client):
    login(client, 1003, 3333)
    response = client.post('/deposit', data={'amount': -100}, follow_redirects=True)
    assert b"Internal Server Error" in response.data  # Since we re-raise exception

def test_withdraw_valid(client):
    login(client, 1004, 4444)
    users[1004]['amount'] = 5000
    response = client.post('/withdraw', data={'amount': 1000}, follow_redirects=True)
    assert users[1004]['amount'] == 4000
    assert b"4000" in response.data

def test_withdraw_insufficient_funds(client):
    login(client, 1005, 5555)
    users[1005]['amount'] = 500
    response = client.post('/withdraw', data={'amount': 1000}, follow_redirects=True)
    assert b"Insufficient balance" in response.data

def test_logout(client):
    login(client, 1001, 1111)
    response = logout(client)
    assert b"Login" in response.data or b"Sign in" in response.data

def test_trigger_exception(client):
    with pytest.raises(ValueError):
        client.get('/trigger-exception')
