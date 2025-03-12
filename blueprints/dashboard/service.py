

from blueprints.users.user_service import UserService


class DashboardService():
    def __init__(self,user_service:UserService) -> None:
        self.user_service = user_service

    def get_username_by_userid(self,user_id:int) -> str:
        username = self.user_service.get_username_by_userid(user_id=user_id)
        return username if username else "Unknown user"