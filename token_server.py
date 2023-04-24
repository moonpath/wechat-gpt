import os
import sys
import time
import json
import logging
import requests


def check_and_update(config: str, period: int = 300):
    try:
        with open(config, "r") as f:
            server_config = json.load(f)

        openids = list(server_config['server_openids'])

        for openid in openids:
            appid = str(server_config[openid]['appid'])
            secret = str(server_config[openid]['secret'])
            expires_in = int(server_config[openid]['expires_in'])
            update_time = float(server_config[openid]['update_time'])

            current_time = time.time()

            if current_time - update_time > expires_in - period:
                req = requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}")
                logging.info(f"request_result: {req.text}")
                req_dict = json.loads(req.text)
                if "access_token" in req_dict:
                    server_config[openid]['update_time'] = float(current_time)
                    server_config[openid]['access_token'] = str(req_dict["access_token"])
                    server_config[openid]['expires_in'] = int(req_dict["expires_in"])
                else:
                    logging.error(f"update: update failed!")
            else:
                logging.info(f"update: still valid.")

        with open(config, "w") as f:
            json.dump(server_config, f, indent=4)
    except Exception as e:
        logging.error(f"update: {e}")
    return


def main():
    os.chdir(sys.path[0])
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    while True:
        check_and_update("server_config.json")
        time.sleep(200)
    pass


if __name__ == "__main__":
    main()