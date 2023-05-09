import logging
import os
import sys
import uvicorn
import hashlib
import jsonutil
import reply
import receive
import handle
from fastapi import FastAPI, Request, BackgroundTasks


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
app = FastAPI()


@app.get("/")
async def root(signature: str, timestamp: str, nonce: str, echostr: str):
    try:
        token = jsonutil.get_json_field("server_config.json", "$.token")
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        sha1.update(list[0].encode("utf-8"))
        sha1.update(list[1].encode("utf-8"))
        sha1.update(list[2].encode("utf-8"))
        hashcode = sha1.hexdigest()  # 获取加密串
        # 验证
        logging.info(f"wechat_server_verify: handle/GET func: hashcode, signature: {hashcode} {hashcode}")
        if hashcode == signature:
            return echostr
        else:
            return ""
    except Exception as e:
        logging.error(f"wechat_server_verify_error: {e}")
        return e
    pass


@app.post("/")
async def post(request: Request, signature: str, timestamp: str, nonce: str, openid: str, backgroundTasks: BackgroundTasks):
    try:
        logging.info(f"url: {openid} {request.url}")
        token = jsonutil.get_json_field("server_config.json", "$.token")
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        sha1.update(list[0].encode("utf-8"))
        sha1.update(list[1].encode("utf-8"))
        sha1.update(list[2].encode("utf-8"))
        hashcode = sha1.hexdigest()
        if hashcode != signature:
            logging.warning(f"wechat_message_verify: {openid} signature is error!")
            return "success"

        rec_msg = receive.parse_xml(await request.body())
        logging.info(f"received_message: {openid} {rec_msg}")
        if isinstance(rec_msg, receive.Msg) and rec_msg.MsgType == 'text':
            rec_content = rec_msg.Content.decode('utf-8')
            customer_openid = rec_msg.FromUserName
            service_openid = rec_msg.ToUserName
            logging.info(f"question: {customer_openid} {rec_content}")
            backgroundTasks.add_task(handle.generate_response, service_openid, customer_openid, rec_content)
            content = "正在思考中..."
            reply_msg = reply.TextMsg(customer_openid, service_openid, content)
            return reply_msg.send()
        else:
            return "success"
    except Exception as e:
        logging.error(f"wechat_receive_error: {e}")
        return e
    pass


if __name__ == "__main__":
    os.chdir(sys.path[0])
    uvicorn.run(app='main:app', host='127.0.0.1', port=8081, reload=True)
