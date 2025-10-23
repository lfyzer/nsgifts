from typing import Any, Dict

from ..enums import HTTPRequestType, UserEndpoint
from ..models import UserLoginSchema, UserSignupSchema


class UserMethods:
    def __init__(self, client):
        self._client = client

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        email = self._client._validate_email(email)
        password = self._client._sanitize_input(password, max_length=255)
        
        self._client.email = email
        self._client.password = password
        
        data = UserLoginSchema(email=email, password=password).model_dump()
        result = await self._client._request_with_retries(
            HTTPRequestType.POST, 
            UserEndpoint.LOGIN, 
            data, 
            is_auth_request=True
        )
        
        self._client.logger.info("User login successful")
        return result

    async def signup(self, username: str, email: str, password: str) -> Dict[str, Any]:
        username = self._client._sanitize_input(username, max_length=50)
        email = self._client._validate_email(email)
        password = self._client._sanitize_input(password, max_length=255)
        
        self._client.email = email
        self._client.password = password
        
        data = UserSignupSchema(username=username, email=email, password=password).model_dump()
        result = await self._client._request_with_retries(
            HTTPRequestType.POST, 
            UserEndpoint.SIGNUP, 
            data, 
            is_auth_request=True
        )
        
        self._client.logger.info("User signup successful")
        return result

    async def check_balance(self) -> Dict[str, Any]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            UserEndpoint.CHECK_BALANCE
        )

    async def get_user_info(self) -> Dict[str, Any]:
        return await self._client._make_authenticated_request(
            HTTPRequestType.POST, 
            UserEndpoint.GET_USER_INFO
        )