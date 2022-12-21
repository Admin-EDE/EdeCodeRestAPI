from datetime import datetime
import requests
from django.conf import settings
from pytz import timezone


def login_otp(run_, otp_):
    now_ = datetime.now(timezone('Chile/Continental'))
    dt_ = now_.strftime('%Y-%m-%dT%H:%M:%S%Z:00')
    tmz_ = int(datetime.timestamp(now_))
    print(f"OTP: {otp_},RUN: {run_}, NOW: {now_}, TZ: {tmz_}, t_:{dt_}")

    url = settings.OTP_SERVICE
    print(url)
    headers = {'Content-Type': 'application/json', 'x-api-key': settings.X_API_KEY}
    payload = [{"RUT": run_, "OTP": otp_, "TIMESTAMP": dt_}]
    req = requests.post(url, headers=headers, json=payload)
    print(f"Request result: {req.status_code}, {req.json()}, {req.reason}")
    r_ = req.json()
    if (req.status_code != 200 or not r_[0].get('OTPVERIFY', False) or r_[0].get(
            'OTPVERIFY') == 'RUT_NO_EXISTE'): return False
    return True

