import os
import requests
import base64
from PIL import Image
import io

def extract_recipt_info(uploaded_file):
    API_KEY = os.environ.get("AZURE_LLM__MODELS__GPT_4_VISION__API_KEY")
    if not API_KEY:
        raise ValueError("Azure API key not found in environment variables")

    # Convert uploaded file to bytes
    img_byte_arr = io.BytesIO()
    image = Image.open(uploaded_file)
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    encoded_image = base64.b64encode(img_byte_arr).decode('ascii')

    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an AI assistant that analyzes images and provides detailed descriptions."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": '''Attached image is a receipt of shopping items  in German language.
                          Analyze this receipt and extract transaction details in English. Item type can be Fruits, dairy, meat etc etc
                            Categories  = [
                            'Housing', 'Utilities', 'Transportation', 'Groceries', 'Healthcare', 'Insurance', 
                            'Savings and Investments', 'Debt Repayment', 'Personal Care', 'Entertainment and Leisure', 
                            'Income', 'Other']. 
                            Categorize each item from transaction into one of the following Categories. If an item doesn't clearly fit into any category, assign it to 'Groceries' by default.If no date, assign current date.
                          Return the answer in JSON format [{{"Item": "Item Name","Item Type": "type, "Quantity": "X", "Amount": "Y", "Category": "Category Name", "Store Name": "Store Name", "Date": "DD-MM-YYYY"}}].
                          Do not include any explanations or other text only json.'''
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    ENDPOINT = os.environ.get("AZURE_LLM__MODELS__GPT_4_VISION__ENDPOINT")
    if not ENDPOINT:
        raise ValueError("Azure endpoint not found in environment variables")

    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        assistant_response = response.json()['choices'][0]['message']['content']
        return assistant_response
    except requests.RequestException as e:
        raise Exception(f"Failed to make the request. Error: {e}")
    except KeyError:
        raise Exception("Unexpected response format from Azure API")