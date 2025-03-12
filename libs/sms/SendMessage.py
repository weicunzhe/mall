from libs.sms import SmsSDK

accId = '2c94811c946f6bfb0195846f61952b7b'
accToken = '6ccc2e2111c0408e96cff3e484c2fb6d'
appId = '2c94811c946f6bfb0195846f63402b82'

def send_message():
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    mobile = '18309252173'
    datas = ('1234', '5')
    resp = sdk.sendMessage(tid, mobile, datas)
    print(resp)

send_message()
