"""User operations - login, signup, balance."""

from ..enums import UserEndpoint, HTTPRequestType
from ..models import (
    LoginResponse,
    SignupResponse,
    UserInfoResponse,
    UserLoginSchema,
    UserSignupSchema,
)


class UserMethods:
    """Handle user stuff like login and checking balance."""

    def __init__(self, client):
        """Initialize with client reference.
        
        Args:
            client: Main NSGiftsClient instance.
        """

        self._client = client


    async def login(self, email: str, password: str) -> LoginResponse:
        """Log in and get your API token.
        
        Token gets saved automatically for future requests.
        
        Args:
            email (str): Your email or username.
            password (str): Your password.
            
        Returns:
            LoginResponse: Login response with access token, expiry, and
                user ID. Access via response.access_token,
                response.valid_thru, response.user_id.
        """

        self._client.email = email
        self._client.password = password
        data = UserLoginSchema(email=email, password=password).model_dump()
        result = await self._client._request_with_retries(
            HTTPRequestType.POST,
            UserEndpoint.LOGIN,
            data,
            is_auth_request=True
        )

        return LoginResponse(**result)


    async def signup(
        self, 
        username: str,
        email: str, 
        password: str
    ) -> SignupResponse:
        """Create new account.
        
        Your account is ready to use immediately after signup.
        
        Args:
            username (str): Username (must be unique).
            email (str): Email address (must be unique).
            password (str): User password.
                
        Returns:
            SignupResponse: Registration response with access token.
                Access via response.access_token, response.token_type.
        """

        self._client.email = email
        self._client.password = password
        data = UserSignupSchema(
            username=username,
            email=email, 
            password=password
        ).model_dump()

        result = await self._client._request_with_retries(
            HTTPRequestType.POST, 
            UserEndpoint.SIGNUP, 
            data, 
            is_auth_request=True
        )

        return SignupResponse(**result)


    async def check_balance(self) -> float:
        """Check your account balance.
        
        Returns:
            float: Current account balance.
        """

        return await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            UserEndpoint.CHECK_BALANCE
        )


    async def get_user_info(self) -> UserInfoResponse:
        """Get your account info.
        
        Returns:
            UserInfo: User profile data. Access via response.id,
                response.username, response.login,
                response.rights, response.balance.
        """

        result = await self._client._make_authenticated_request(
            HTTPRequestType.POST,
            UserEndpoint.GET_USER_INFO
        )
        return UserInfoResponse(**result)