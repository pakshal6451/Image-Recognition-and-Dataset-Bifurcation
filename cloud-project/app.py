from flask import Flask, render_template, request, redirect, url_for
import boto3
import requests
import json

app = Flask(__name__)

S3_BUCKET = 'pakshal-b00935061-images'
S3_ACCESS_KEY = 'ASIATCG46ZXRB7OVLELB'
S3_SECRET_KEY = 'Xu/PhwTVDR8NHywC9FgyovL/2y/g8YrnxIAX2DzA'
S3_SESSION_TOKEN = 'FwoGZXIvYXdzEPb//////////wEaDMgYyLvj+7xzKVTrKiLAAWmBYHpW2TYzRzfW8XbcLrtgCYHAZerzkXoPJyCxsZzyO68LeBb13ytSiljCFDfYjb1UKh6Q5o97n7SydON50o5EkHKkOEDuRRet4Cn6xC5EeNHmYpl2PAWUvKOvN+3KxUSoAJUi+hwkeNoUUdHOCAGG6zoR2dfUMEFmYwp+JdEzAIEEtBWU/ncdgtbtM9RJvSb9vab2+ehHPYkYy4UMZGSO5wA3aIZ9v7i8wX3/P/aRUP+icJU42e+t1Al2oM5edCjov5CmBjItDgO+bpcmdFNJL1ZzmjSkZ6dbayhHyNPN6D0hgKQKfIyxidwWWxukOWnCiQmT'  
S3_LOCATION = f'http://{S3_BUCKET}.s3.amazonaws.com/'
API_ENDPOINT = "https://re7padjoo7.execute-api.us-east-1.amazonaws.com/get-data" 

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
