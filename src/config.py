import os
ws_user_accounts = [
    {
        "username": os.getenv('WS_USERNAME_1'),
        "password": os.getenv('WS_PASSWORD_1'),
        "client_id": os.getenv('WS_CLIENT_ID_1'),
        "ws_otp_claim": os.getenv('WS_OTP_CLAIM_1'),
        "ws_user_session_id": os.getenv('WS_USER_SESSION_ID_1'),
        "ws_device_id": os.getenv('WS_DEVICE_ID_1')
    },
    {
        "username": os.getenv('WS_USERNAME_2'),
        "password": os.getenv('WS_PASSWORD_2'),
        "client_id": os.getenv('WS_CLIENT_ID_2'),
        "ws_otp_claim": os.getenv('WS_OTP_CLAIM_2'),
        "ws_user_session_id": os.getenv('WS_USER_SESSION_ID_2'),
        "ws_device_id": os.getenv('WS_DEVICE_ID_2')
    }
]
