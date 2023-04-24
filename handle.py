import logging
import jsonutil
import openaiutil
import requests
import json


def generate_response(service_openid: str, customer_openid: str, content: str):
    try:
        answer = openaiutil.chat(content, customer_openid)
        logging.info(f"answer: {customer_openid} {answer}")
        data = {
            "touser": customer_openid,
            "msgtype": "text",
            "text":
                {
                    "content": answer
                }
        }
        access_token = jsonutil.get_json_field("server_config.json", f"$.{service_openid}.access_token")
        res = requests.post(f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}",
                            data=bytes(json.dumps(data, ensure_ascii=False), encoding='utf-8'))
        logging.info(f"wechat_send_result: {customer_openid} {res.text}")
    except Exception as e:
        logging.error(f"generate_response: {e}")
    return
