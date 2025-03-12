

from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService


class DashboardService():
    def __init__(self,user_service:UserService, mfa_service = MFAservice) -> None:
        self.user_service = user_service
        self.mfa_service = mfa_service

    def get_username_by_userid(self,user_id:int) -> str:
        username = self.user_service.get_username_by_userid(user_id=user_id)
        return username if username else "Unknown user"
    
    def is_mfa_enabled(self, user_id: int) -> bool:
        return bool(self.mfa_service.get_mfa_details_via_user_id(user_id=user_id))