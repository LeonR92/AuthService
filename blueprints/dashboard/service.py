"""Dashboard Service Module.

This module provides the DashboardService class which handles dashboard-related 
operations by coordinating between user management and multi-factor authentication 
services. It serves as an abstraction layer to expose only the necessary functionality 
to dashboard controllers while encapsulating the underlying service interactions.
"""

from blueprints.users.mfa_service import MFAservice
from blueprints.users.user_service import UserService


class DashboardService():
    """Dashboard management service for user information and authentication status.
    
    This service provides an interface to retrieve user data and authentication
    status information required by dashboard views. It acts as a facade over 
    the user and MFA services, centralizing access to these dependencies and
    providing consistent error handling and data normalization.

    """
    def __init__(self,user_service:UserService, mfa_service = MFAservice) -> None:
        """Initialize the dashboard service with required dependencies.
        
        :param user_service: Service for accessing and managing user data
        :type user_service: UserService
        :param mfa_service: Service for managing multi-factor authentication
        :type mfa_service: MFAservice
        """
        self.user_service = user_service
        self.mfa_service = mfa_service

    def get_username_by_userid(self,user_id:int) -> str:
        """Retrieve a user's display name from their unique identifier.
        
        This method attempts to fetch the username associated with the provided
        user ID. It implements defensive programming by returning a fallback value
        when the username cannot be retrieved rather than propagating exceptions
        or returning None.
        
        :param user_id: The unique identifier of the user
        :type user_id: int
        :return: The username if found, otherwise "Unknown user"
        :rtype: str

        Usage example:
        username = dashboard_service.get_username_by_userid(user_id=user_id)
        """
        username = self.user_service.get_username_by_userid(user_id=user_id)
        return username if username else "Unknown user"
    
    def is_mfa_enabled(self, user_id: int) -> bool:
        """Determine if multi-factor authentication is enabled for a user.
        
        Checks the MFA status for the specified user by attempting to retrieve
        their MFA details. The result is normalized to a boolean value for
        consistent interface regardless of the underlying implementation details.
        
        :param user_id: The unique identifier of the user
        :type user_id: int
        :return: True if MFA is enabled for the user, False otherwise
        :rtype: bool

        Usage example:
        mfa_enabled = dashboard_service.is_mfa_enabled(user_id=user_id)
        """
        return bool(self.mfa_service.get_mfa_details_via_user_id(user_id=user_id))