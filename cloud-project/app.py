from flask import Flask, render_template, request, redirect, url_for
import boto3
import requests
import json

app = Flask(__name__)

S3_BUCKET = 'pakshal-b00935061-images'
S3_ACCESS_KEY = 'ASIATCG46ZXROB6UUGNI'
S3_SECRET_KEY = 't4o0tksHpyozGa6DsnfS3t6yNdOFq8ihgcO2/pBJ'
S3_SESSION_TOKEN = 'FwoGZXIvYXdzEPD//////////wEaDKgZCTUzA937QNllKSLAATqCfoTl2AZSzXuq1aTLkDDQy8sR1uxtWWoKxVJ6+vOyA5sDIZVz8WZL2zVacaHbKcx6j0ND7uaTJdFNWVe8SAZXou+kpqk4VmS6mvb9aHxduThLkbGECeloDps1wcN6G/WTahOgsgjvVg6kgLg5iGNjiRsXTQr/RSNO+fPuZjoQW9U6u+jBzUXL7pFniaHQ/j0yH6hV3m/X4eZ9U5DuXVp4ENAYQ0cH6rkEEept++ufEl9Sz7UzQFvaqPcnzZhKzSiCro+mBjIt0+RZjqvT8PKatjZso2eXcGjLw/dsv28SHrPhh+N/iA+dlRzeGJUGpG00Yr5H'  
S3_LOCATION = f'http://{S3_BUCKET}.s3.amazonaws.com/'
# API_ENDPOINT = "https://re7padjoo7.execute-api.us-east-1.amazonaws.com/get-data" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        aws_session_token=S3_SESSION_TOKEN
    )

    file = request.files['file']

    if file:
        filename = file.filename
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        return redirect(url_for('view_images'))

    return f"Failed to upload {filename}."

def categorize_images(data):
    categories = {
        "Person": [],
        "Animal": [],
        "Flower": [],
        "Others": []
    }

    for item in data:
        item["url"] = f"https://{item['bucket']}.s3.amazonaws.com/{item['ImageName']}"
        if any(label["label"] == "Person" for label in item["labels_data"]):
            categories["Person"].append(item)
        elif any(label["label"] == "Animal" for label in item["labels_data"]):
            categories["Animal"].append(item)
        elif any(label["label"] == "Flower" for label in item["labels_data"]):
            categories["Flower"].append(item)
        else:
            categories["Others"].append(item)

    return categories

@app.route('/view-images')
def view_images():
    try:
        response = requests.get(API_ENDPOINT)
        data = json.loads(response.json()["body"])
        
        categorized_images = categorize_images(data)
        return render_template('view_images.html', categories=categorized_images, error=None)

    except Exception as e:
        print("Error fetching images:", e)
        return render_template('view_images.html', categories={}, error=str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
