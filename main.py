import boto3
import re
import numpy as np
import cv2
from PIL import Image
import io
import os
from io import BytesIO
from botocore.exceptions import NoCredentialsError
import uuid
import string
import random

AWS_ACCESS_KEY_ID = 'AKIA5WJN5H4WJH4HUJGA'
AWS_SECRET_ACCESS_KEY = '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'

s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = "pic-input"
input_image = "input-folder/18.jpg"


def image_from_s3(key):
    bucket_test = s3.Bucket(bucket)
    image = bucket_test.Object(key)
    img_data = image.get().get('Body').read()
    return Image.open(io.BytesIO(img_data))

def test(key):
    bucket_test = s3.Bucket(bucket)
    img = bucket_test.Object(key).get().get('Body').read()
    nparray = cv2.imdecode(np.asarray(bytearray(img)), cv2.IMREAD_COLOR)

    return nparray


def img_pixel():
    rec = image_from_s3(input_image)
    print(rec)
    width, height = rec.size

    return rec.size

def upload_to_aws(local_file, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

def img_mask(tlx1, tly, brx1, bry, image):
    start_point = (tlx1+50, tly)
    end_point = (brx1-10, bry)
    color = (0, 0, 0)
    thickness = -1

    print(type(image))

    image1 = cv2.rectangle(image, start_point, end_point, color, thickness)

    img_name  = get_random_string(8)
    print(img_name)

    cv2.imwrite("E:/Rekognition test/output-image/"+img_name+".jpg", image1)
    print(image1)
    print(f'image1 type: {type(image1)}')
    img = Image.fromarray(image1).convert("RGB")
    out_img = BytesIO()
    img.save(out_img, format='png')
    out_img.seek(0)

    uploaded = s3.Bucket(bucket).put_object(Key='output-folder/'+img_name+'.jpg', Body=out_img, ContentType='image/png', ACL='public-read')

    #uploaded = upload_to_aws(out_img, "pic-input", "img_masked")
    print(uploaded)


def detect_text(photo):
    client = boto3.client('rekognition')

    response = client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    textDetections = response['TextDetections']
    #print('Detected text\n----------')
    regex = ("^[2-9]{1}[0-9]{3}\\" +
             "s[0-9]{4}\\s[0-9]{4}$")
    p = re.compile(regex)

    for text in textDetections:
        if text['Type'] == "LINE":
            if (re.search(p, text['DetectedText'])):
                print('Detected text:' + text['DetectedText'])
                #print(text['Geometry']["Polygon"])

                width, height = img_pixel()
                print(f'width: {width}\nheight: {height}')


                data = text['Geometry']["Polygon"]
                print(data)
                one = data[0]
                third = data[2]

                print(one, third)

                x1 = one["X"]
                y1 = one["Y"]
                x2 = third["X"]
                y2 = third["Y"]
                print(x1,y1, x2, y2)

                tlx = x1*width
                tlx1 = int(0.85*tlx)
                tly = int(y1*height)

                brx = x2 * width
                brx1 = int(0.85*brx)
                bry = int(y2 * height)

                print(tlx1, tly)
                print(brx1, bry)

                image = image_from_s3(input_image)
                print(type(image))
                print(image.format)
                numpyarr = test(input_image)

                numpydata = np.array(image)
                print(numpydata)

                img_mask(tlx1, tly, brx1, bry,  numpyarr)


def main():
    photo = input_image
    text_count = detect_text(photo)

if __name__ == "__main__":
    main()