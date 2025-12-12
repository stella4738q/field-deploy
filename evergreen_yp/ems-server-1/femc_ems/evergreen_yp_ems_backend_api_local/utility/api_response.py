class ApiResponse:
    def __init__(self, success=True, msg='Success', rtn_data=None):
        self.Success = success
        self.Msg = msg
        self.Data = rtn_data

    @property
    def serialized(self):
        return self.__dict__


class TokenResponse(ApiResponse):
    def __init__(self, success=True, msg='Success', rtn_data=None, token=None, user_info=None, field_id=None):
        super().__init__(success, msg, rtn_data)
        self.Token = token
        self.FieldId = field_id
        self.UserInfo = user_info
        self.Otp = False
