import openai
import jsonutil
import logging


def chat(content: str, openid: str):
    openai.api_key = jsonutil.get_json_field("openai_config.json", "$.api_key")
    times = 0
    while times < 3:
        times += 1
        try:
            response = openai.ChatCompletion.create(
                max_tokens=1000,
                model="gpt-3.5-turbo",
                messages=[
                    # {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": content},
                    # {"role": "assistant", "content": "Today is monday."},
                ],
                user=openid,
            )

            answer = response.choices[0].message.content.strip()
            break
        except Exception as e:
            logging.error(f"openai_error: {e}")
    else:
        answer = "出了点小故障，请重新提问"
    return answer