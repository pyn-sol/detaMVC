from fastapi import Request
from fastapi.responses import RedirectResponse
from detamvc.model import DetaModel, Alert
from user.utils import Auth, current_user


auth_handler = Auth()


class User(DetaModel):
    username: str
    password: str

    class Config:
        table_name = "{proj}_user"

    @classmethod
    def fetch_user(cls, username: str):
        user = cls.query({{'username': username}})
        if user:
            return user[0]
        return False

    def signup(self):
        if User.fetch_user(self.username):
            return Alert('An account with that username already exists.')
        else:
            try:
                hashed_password = auth_handler.encode_password(self.password)
                self.password = hashed_password
                self.save()
                return Alert('Success! Please login.', 'success')
            except:
                return Alert('Failed to signup User.')

    @classmethod
    def new_user(cls, email):
        data = {{
            'username': email,
            'password': 'N/A'
        }}
        user = User.parse_obj(data)
        user.save()
        return user

    @classmethod
    def signup_from_google_login(cls, email):
        user = cls.fetch_user(email)
        if not user:
            user = cls.new_user(email)
        return user

    def create_session(self, request: Request):
        access_token = auth_handler.encode_token(self.key)
        refresh_token = auth_handler.encode_refresh_token(self.key)
        results = {{
            'access_token': access_token,
            'refresh_token': refresh_token}}

        request.session['user'] = results
        request.session['user'].update(self.dict())

    def login(self, request: Request):
        find_user = User.query({{'username': self.username}})
        alert = Alert('Invalid Username or Password')
        if find_user:
            user = find_user[0]
        else:
            return alert
        if not auth_handler.verify_password(self.password, user.password):
            return alert

        user.create_session(request)
        return RedirectResponse('/user/dashboard', 303)

    @classmethod
    def refresh_token(cls, request: Request):
        user = current_user(request)
        refresh_token = user['refresh_token']
        return auth_handler.refresh_token(refresh_token)