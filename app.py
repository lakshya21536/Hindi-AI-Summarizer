from flask import Flask, render_template, request
import requests
import time
import os

app = Flask(__name__)

# Hugging Face API URLs and tokens
API_URLS = {
    "mT5": "https://api-inference.huggingface.co/models/lakshya188/mt5_finetuned",
    "IndicBART": "https://api-inference.huggingface.co/models/lakshya188/indicBART_finetuned"
}
HEADERS = {"Authorization": "Bearer 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"}  # Replace with your actual Hugging Face API token

def query_huggingface_api(model_name, payload):
    retries = 5
    for i in range(retries):
        response = requests.post(API_URLS[model_name], headers=HEADERS, json=payload)
        result = response.json()
        
        if "error" not in result:
            return result
        
        error_message = result.get("error")
        if error_message == "Model is currently loading":
            time.sleep(10)  # Wait for 10 seconds before retrying
        else:
            return {"error": error_message}
    
    return {"error": "Model loading timeout"}


def get_response(article, model):
    if article.strip() == "":
        return "Input text is empty. Please provide some text to summarize."

    payload = {"inputs": article}
    output = query_huggingface_api(model, payload)

    if "error" in output:
        return "Error: " + output["error"]
    
    if isinstance(output, list) and len(output) > 0:
        summary_text = output[0].get("generated_text", "No summary available")
        return summary_text
    else:
        return "Error: Unexpected response format or empty response"


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/summarize", methods=['POST'])
def summarize():
    if request.method == 'POST':
        input_text = request.form['text']
        model_selected = request.form['model_selected']
        summarized = get_response(input_text, model_selected)
        return render_template('index.html', input_text=input_text, summarized=summarized)
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
