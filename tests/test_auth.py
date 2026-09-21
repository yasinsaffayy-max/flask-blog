from app.models import User


class TestLogin:
    def test_login_page(self, client):
        r = client.get('/auth/login')
        assert r.status_code == 200

    def test_login_success(self, client, admin):
        r = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_wrong_password(self, client, admin):
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrong',
        }, follow_redirects=True)
        with client.session_transaction() as sess:
            assert '_user_id' not in sess

    def test_login_nonexistent(self, client, db):
        client.post('/auth/login', data={
            'username': 'nobody',
            'password': 'any',
        }, follow_redirects=True)
        with client.session_transaction() as sess:
            assert '_user_id' not in sess


class TestLogout:
    def test_logout(self, admin_client):
        r = admin_client.get('/auth/logout', follow_redirects=True)
        assert r.status_code == 200
        r2 = admin_client.get('/admin/')
        assert r2.status_code == 302
