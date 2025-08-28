from src.models.auth import Auth
class AuthRepository:
    def __init__(self, db):
        self.db = db

    def get_user_by_username(self, user_name):
        """get user by the username"""
        return  self.db.query(Auth).filter(Auth.username == user_name).first()
    def get_user_by_id(self, user_id):
        """get user by the id"""
        return  self.db.query(Auth).filter(Auth.id == user_id).first()
    def create_user(self, user):
        """create a new user"""
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            print(f'create user failed auth repo {e}')
            raise e
