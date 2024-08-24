import os
from openai import OpenAI
import base64
from PIL import Image
import io

def extract_recipt_info(uploaded_file):
    API_KEY = os.environ.get("OPENAI_API_KEY")
    if not API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")

    client = OpenAI(api_key=API_KEY)

    img_byte_arr = io.BytesIO()
    image = Image.open(uploaded_file)
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    encoded_image = base64.b64encode(img_byte_arr).decode('ascii')

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that analyzes images and provides detailed descriptions."
                },
                {
                    "role": "user",
                    "content": {
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                            "alt_text": "Receipt image for analysis"
                        }
                    }
                },
                {
                    "role": "user",
                    "content": '''Analyze this receipt and extract transaction details in English. 
                        Categories = [
                        'Housing', 'Utilities', 'Transportation', 'Groceries', 'Healthcare', 'Insurance', 
                        'Savings and Investments', 'Debt Repayment', 'Personal Care', 'Entertainment and Leisure', 
                        'Income', 'Other']. 
                        Categorize each item from transaction into one of the following Categories. If an item doesn't clearly fit into any category, assign it to 'Groceries' by default.
                        Item type can be Fruits, dairy, meat, vegetable, fastfood etc etc, These are like sub category. If no date, assign current date.
                      Return the answer in JSON format [{"Item": "Item Name","Item Type": "type, "Quantity": "X", "Amount": "Y", "Category": "Category Name", "Store Name": "Store Name", "Date": "DD-MM-YYYY"}].
                      Do not include any explanations or other text only json.'''
                }
            ],
            max_tokens=800
        )
        
        assistant_response = response.choices[0].message.content
        return assistant_response
    except Exception as e:
        raise Exception(f"Failed to make the request. Error: {e}")