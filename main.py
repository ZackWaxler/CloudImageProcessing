import os
from flask import Flask
from flask import render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

from PIL import Image, ImageOps, ImageFilter

import boto3
import logging
from botocore.exceptions import ClientError
from boto3.s3.transfer import S3Transfer

UPLOAD_FOLDER = './temp_storage'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '123456'

def upload_file(file_name, bucket, object_name=None):
	if object_name is None:
		object_name = file_name

	s3_client = boto3.client('s3')
	transfer = S3Transfer(s3_client)

	pub_url = None

	try:
		response = transfer.upload_file(file_name, bucket, object_name, extra_args={'ACL': 'public-read'})
		pub_url = f'https://{bucket}.s3.amazonaws.com/{object_name}'
	except ClientError as e:
		logging.error(e)
		return False
	return pub_url

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
  return render_template('index.jinja.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		print(request.files)

		file = request.files['image']

		if file and allowed_file(file.filename):
			filters = []

			form = request.form.to_dict()

			if 'gray' in form: filters.append('gray') 
			if 'blur' in form: filters.append('blur') 
			if 'solar' in form: filters.append('solar')

			# Save image to temp folder with unique name
			uid = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
			filename = secure_filename(file.filename)
			new_name = filename.split('.')[0] + '_' + uid + '.' + filename.split('.')[1]
			path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
			file.save(path)

			gray_url = '-'
			blur_url = '-'
			solar_url = '-'

			# for each filter
			# - Apply it & save to tmp
			for filter_type in filters:
				img = Image.open(path)

				if filter_type == 'gray':
					img = ImageOps.grayscale(img)	
				
				if filter_type == 'blur':
					img = img.filter(ImageFilter.BLUR)		

				if filter_type == 'solar':
					img = ImageOps.solarize(img, threshold=80) 

				new_path = path.replace(uid, uid + '_' + filter_type)
				filtered_name = new_name.replace(uid, uid + '_' + filter_type)

				img.save(new_path)

				pub_url = upload_file(new_path, 'cip-zw', object_name=filtered_name)
				if filter_type == 'gray': gray_url = pub_url
				elif filter_type == 'blur': blur_url = pub_url
				elif filter_type == 'solar': solar_url = pub_url

			return redirect(url_for('uploaded', gray=gray_url, blur=blur_url, solar=solar_url))
		return redirect(url_for('error')) # Error with file
	return redirect(url_for('error')) # GET request

@app.route('/uploaded')
def uploaded():
	return render_template('uploaded.jinja.html', gray=request.args.get('gray'), blur=request.args.get('blur'), solar=request.args.get('solar'))
	# return request.args.get('gray') + ' ' + request.args.get('blur') + ' ' + request.args.get('solar')

@app.route('/error')
def error():
	return 'An error occurred. Redirecting.<script>setTimeout(() => { window.location = "/"; }, 1000)</script>'

# Disable caching static resources
# Snippet from https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(req):
	req.headers['Pragma'] = 'no-cache'
	req.headers['Expires'] = '0'
	req.headers['Cache-Control'] = 'public, max-age=0'
	return req
