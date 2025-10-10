"""User operations - login, signup, balance."""

from typing import Any, Dict

from ..models import UserLoginSchema, UserSignupSchema


class UserEndpoints:
    """Handle user stuff like login and checking balance."""
    
    BASE_PATH = "/api/v1"
    
    @staticmethod
    def get_endpoints() -> Dict[str, str]:
        """Get API endpoint URLs.
        
        Returns:
            Dict[str, str]: Dictionary mapping operation names to their
                endpoint URLs.
        """
        return {
            "login": f"{UserEndpoints.BASE_PATH}/get_token",
            "signup": f"{UserEndpoints.BASE_PATH}/signup", 
            "check_balance": f"{UserEndpoints.BASE_PATH}/check_balance",
            "get_user_info": f"{UserEndpoints.BASE_PATH}/user",
        }

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """
        self._client = client

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Log in and get your API token.
        
        Token gets saved automatically for future requests.
        
        Args:
            email (str): Your email or username.
            password (str): Your password.
            
        Returns:
            Dict[str, Any]: Login response with access token.
        """
        self._client.email = email
        self._client.password = password
        data = UserLoginSchema(email=email, password=password).model_dump()
        return await self._client._request_with_retries(
            "POST", 
            self.get_endpoints()["login"], 
            data, 
            is_auth_request=True
        )

    async def signup(
        self, 
        username: str,
        email: str, 
        password: str
    ) -> Dict[str, Any]:
        """Create new account.
        
        Your account is ready to use immediately after signup.
        
        Args:
            username (str): Username (must be unique).
            email (str): Email address (must be unique).
            password (str): User password.
                
        Returns:
            Dict[str, Any]: Registration response with access token.
        """
        self._client.email = email
        self._client.password = password
        data = UserSignupSchema(
            username=username,
            email=email, 
            password=password
        ).model_dump()
        return await self._client._request_with_retries(
            "POST", 
            self.get_endpoints()["signup"], 
            data, 
            is_auth_request=True
        )

    async def check_balance(self) -> Dict[str, Any]:
        """Check your account balance.
        
        Returns:
            Dict[str, Any]: Current balance info.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["check_balance"]
        )

    async def get_user_info(self) -> Dict[str, Any]:
        """Get your account info.
        
        Returns:
            Dict[str, Any]: User profile data.
        """
        return await self._client._make_authenticated_request(
            "POST", 
            self.get_endpoints()["get_user_info"]
        )
