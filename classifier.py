# type:ignore
# flake8: noqa
import base64
from pathlib import Path
from sys import path_hooks
import cv2
import numpy as np
import os
import dotenv
dotenv.load_dotenv()
trash_present = False
trash_can = False
from PIL import Image
import boto3

client = boto3.client(
    'rekognition',
    region_name="us-east-1",
    aws_access_key_id= os.getenv("aws_access_key_id"),
    aws_secret_access_key= os.getenv("aws_secret_access_key")
)

trash = [
"Trash",
"Bottle",
"Alcohol",
"Beer Bottle",
"Beverage",
"Box",
"Broom",
"Can",
"Diaper",
'Doormat',
'Drawer',
'Durian',
'Flower Bouquet',
'Football',
'Guitar',
'Furniture',
'Handbag',
'Ink Bottle',
'Kettle',
'Kite',
'Luggage',
'Magazine',
'Mat',
'Mattress',
'Milk Can',
'Monitor',
'Newspaper',
'Plastic',
'Plastic Bag',
'Plastic Wrap',
'Radio',
'Sandal',
'Shoe',
'Shovel',
'Skateboard',
'Soccer Ball',
'Suitcase',
'Table Lamp',
'Television',
'Toaster',
'Toy',
'TV',
'Umbrella',
'Vase']


labelsOnly = []
isThereTrash = False
isThereATrashCan = False
trashPresent = []

def label_detections(img):
    global allLabels

    imageByteString = img.tobytes()

    img_as_np = np.frombuffer(imageByteString, dtype=np.uint8)
    img = cv2.imdecode(img_as_np, flags=-1)

    base64_img = base64.b64encode(imageByteString)
    base_64_binary = base64.decodebytes(base64_img)

    response = client.detect_labels(Image={'Bytes': base_64_binary})

    allLabels = response["Labels"]
    return check_if_trash(allLabels)


def check_if_trash(list_):
    print('ssss')

    global trash_can
    global trash_exists
    for i in range(len(list_)):
        label = list_[i-1]
        if label == "Trash Can":
            trash_can = True
        if label == "Can":
            trash_can = True
            list_.pop(i-1)
    if trash_can == True:
        for i in range(len(list)):
            for piece in range(len(trash)):
                pieceOfTrash = trash[piece-1]
                label = list_[i-1]
                if label == pieceOfTrash:
                    trash_exists = True
                    trash_present.append(pieceOfTrash)
    if trash_can == True:
        if trash_exists == True:
            return 'OVERFLOW'
        else:
            return 'EMPTY'
    else:
        return 'EMPTY'


def checkifisitfull():
    global trash_can
    trash_can = True
    for i in range(len(list_)):
        for piece in range(len(trash)):
            pieceOfTrash = trash[piece-1]
            label = list[i-1]
            if label == pieceOfTrash:
                trash_exists = True
            if trash_exists == True:
                print("Bin is full")
            else:
                print("Bin is not full")


def get_state(path: Path):
    img = cv2.imread(path)
    return label_detections(img)



if __name__ == '__main__':
    print(get_state('./img/1.jpg'))
