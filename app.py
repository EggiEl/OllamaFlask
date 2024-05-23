import requests
import json
from flask import Flask, request, jsonify
import os 
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv('SERVER_SECRET')

app = Flask(__name__)
url = 'http://localhost:11434/api/generate'



def send_post_request(url, data):
    response = requests.post(url, json=data, stream=True)
    return response

def handle_streaming_response(response):
    prompt = ""
    if response.status_code == 200:
        try:
            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = json.loads(chunk.decode('utf-8'))
                    prompt += decoded_chunk['response']
                    if decoded_chunk.get('done', False):
                        return prompt
        except Exception as e:
            print("Error while streaming the data:", e)
            return None
    else:
        print("Failed to get response, status code:", response.status_code)
        return None

@app.route('/', methods=['POST'])
def post_method():

    if request.headers.get('secret') != SECRET:
        return jsonify({'error': 'Unauthorized'}), 401
    request_data = request.get_json()
    print("Request data : ", request_data["prompt"])

    data = {
    "model": "llama3",
    "prompt": request_data['prompt'],
    "max_tokens": 200
}
    print("Request received")
    answer = send_post_request(url, data)
    print("Answer : ",  answer)
    final_prompt = handle_streaming_response(answer)
    if final_prompt:
        print(final_prompt)

        return jsonify({'result': final_prompt }), 200
    else:
        return jsonify({'error': 'Failed to generate prompt'}), 500
    




if __name__ == '__main__':
    app.run(debug=True)