WEB_URL = "https://web-api.hypergryph.com"
BASIC_URL = "https://ak.hypergryph.com"
API_URL = "https://as.hypergryph.com"

# 通过 WEB_URL 获取 /account/info/hg 的 content 用于查询抽卡记录的 token
GET_AUTHKEY_URL = WEB_URL + "/account/info/hg"
GET_AUTHKEY_URL_Bilibili = WEB_URL + "/account/info/ak-b"

GET_GACHA_LOG_URL = BASIC_URL + "/user/api/inquiry/gacha"

GET_UID_URL = API_URL + "/u8/user/info/v1/basic"

GET_RECHARGE_RECORD_URL = API_URL + "/u8/pay/v1/recent"
