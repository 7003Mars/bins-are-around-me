
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Union
import csv
from itertools import chain
import logging
from typing import Optional

import boto3
from mypy_boto3_rekognition import RekognitionClient
from mypy_boto3_rekognition.type_defs import DetectLabelsResponseTypeDef, LabelTypeDef
from PIL import Image
from PIL.Image import Image as PImage

from dotenv import load_dotenv
load_dotenv()
client: RekognitionClient = boto3.client(
    'rekognition', region_name='us-east-1')  # Credentials in ~/.aws/credentials
with open('trash_labels.csv', 'r') as f:
    trash_labels: set[str] = set(chain.from_iterable(csv.reader(f)))


class States(Enum):
    EMPTY = 1
    FULL = 2
    OVERFLOW = 3


# TODO: Figure out why mypy isnt type checking this. Found: The 2 arguments were not actually kwargs
def get_state_result(*, image: PImage = None, path: Union[Path, str] = None) -> States:
    # Protip: Path vs path
    if path is not None:
        image = Image.open(path)
    assert image is not None, 'Either image or path must be provided'
    bytes_: BytesIO = BytesIO()
    print(bytes_.writable())
    image.save(bytes_, format='JPEG')
    bytes_.seek(0)
    response: DetectLabelsResponseTypeDef = client.detect_labels(
        Image={'Bytes': bytes_.read()})
    logging.debug(f'Labels: {response["Labels"]}')

    bin_: Optional[LabelTypeDef] = None
    detected_trash: list[LabelTypeDef] = []
    for label in response['Labels']:
        if label['Name'].lower() == 'trash can':
            bin_ = label
        elif label['Name'] in trash_labels:
            detected_trash.append(label)
    if bin_ is None:
        return States.OVERFLOW  # Assume something is covering the bin
    if len(detected_trash) == 0:
        return States.EMPTY
    # TODO: Do bounding box magic here and figure out if there is trash near the bin
    return States.OVERFLOW if set((label['Name'].lower() for label in detected_trash)).issubset(trash_labels) else States.EMPTY


if __name__ == '__main__':
    print(get_state_result(path='./img/1.jpg'))
