#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Bassem Jadoui (bassem.jadoui@esprit.tn)
Flask API to return random meme images
"""

import random

import requests
from bs4 import BeautifulSoup
from flask import Flask, send_file, request
from PIL import Image
from io import BytesIO
import os


from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = './UPLOAD_FOLDER'
uploads_dir = app.config['UPLOAD_FOLDER']


def get_new_memes():
    """Scrapers the website and extracts image URLs

    Returns:
        imgs [list]: List of image URLs
    """
    imgs = []

    """ List of the website to scrape """
    url = 'https://www.memedroid.com/memes/tag/programming'
    url2 = 'https://www.cometchat.com/blog/programming-memes-for-developers'
    url3 = 'https://www.testbytes.net/blog/programming-memes/'


    """ Get the response of every url """
    response = requests.get(url)
    response2 = requests.get(url2)
    response3 = requests.get(url3)


    soup = BeautifulSoup(response.content, 'lxml')
    soup2 = BeautifulSoup(response2.content, 'lxml')
    soup3 = BeautifulSoup(response3.content, 'lxml')



    divs = soup.find_all('div', class_='item-aux-container')
    figures = soup2.find_all('figure', class_='w-richtext-figure-type-image w-richtext-align-fullwidth')
    divs2 = soup3.find_all('img', class_='alignnone')


    for div in divs:
        img = div.find('img')['src']
        if img.startswith('http') :
            imgs.append(img)

    for figure in figures:
        img = figure.find('img')['src']
        if img.startswith('http') :
            imgs.append(img)

    for div in divs2:
        img = div['src']
        imgs.append(img)

    return imgs



def serve_pil_image(pil_img):
    """Stores the downloaded image file in-memory
    and sends it as response

    Args:
        pil_img: Pillow Image object

    Returns:
        [response]: Sends image file as response
    """
    img_io = BytesIO()
    pil_img.convert('RGB').save(img_io, 'JPEG', quality=100, optimize=True)
    img_io.seek(0)
    # download the image to UPLOAD_FOLDER directory


    return send_file(img_io, mimetype='image/jpeg')


def compare_images(input_image, output_image):
  # compare image dimensions (assumption 1)
  if input_image.size != output_image.size:
    return False

  rows, cols = input_image.size

  # compare image pixels (assumption 2 and 3)
  for row in range(rows):
    for col in range(cols):
      input_pixel = input_image.getpixel((row, col))
      output_pixel = output_image.getpixel((row, col))
      if input_pixel != output_pixel:
        return False

  return True

@app.after_request
def set_response_headers(response):
    """Sets Cache-Control header to no-cache so GitHub
    fetches new image everytime
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/", methods=['GET'])
def return_meme():
    imgs = os.listdir(uploads_dir)
    img = random.choice(imgs)
    # get mimetype of the image
    mimetype = img.split('.')[-1]
    if mimetype == 'mp4':
        return send_file(os.path.join(uploads_dir, img), mimetype='video/'+mimetype)
    return send_file(os.path.join(uploads_dir, img), mimetype='image/'+mimetype)



@app.route("/upload", methods=['GET'])
def upload_file():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="/upload" method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route("/fetchMore", methods=['GET'])
def fetchMore():
    # compare the image with the old ones in UPLOAD_FOLDER and store if not exist
    imgs = get_new_memes()
    for img in imgs:
        response = requests.get(img)
        # store the original with the same size and format
        img = Image.open(BytesIO(response.content))
        isExist = False
        for file in os.listdir(uploads_dir):
                image1 = Image.open(os.path.join(uploads_dir, file))
                if compare_images(img, image1):
                    isExist = True
                    break
        if not isExist:
            img.save(os.path.join(uploads_dir, str(len(os.listdir(uploads_dir))) + '.'+img.format.lower()))


    return "Done"





