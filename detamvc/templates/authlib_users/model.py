from datetime import date

from detamvc.model import DetaModel, ItemNotFound


class User(DetaModel):
    created_date: str

    class Config:
        table_name = "{proj}_{obj}"
    
    @classmethod
    def new_user(cls, email):
        data = {{
            'key': email,
            'created_date': str(date.today())
        }}
        user = User.parse_obj(data)
        user.save()
        return user
    
    @classmethod 
    def fetch_or_create(cls, email):
        try:
            user = cls.get(email)
        except ItemNotFound: 
            user = cls.new_user(email)
        return user