import requests

def get_response(url, token, system_prompt, input, prev_id=None):
    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemma-4-e4b",
                "input": input,
                "system_prompt": system_prompt,
                "previous_response_id": prev_id
            }
        )

        message_content = next(item["content"] for item in response.json()["output"] if item["type"] == "message")
        response_id = response.json()["response_id"]

        return message_content, response_id
    except:
        return None