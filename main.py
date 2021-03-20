import os
from flask import Flask
from flask import render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

import boto3

import logging
from botocore.exceptions import ClientError

UPLOAD_FOLDER = './temp_storage'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg' }

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '123456'

def upload_file(file_name, bucket, object_name=None):
	# If S3 object_name was not specified, use file_name
	if object_name is None:
		object_name = file_name

	# Upload the file
	s3_client = boto3.client('s3')
	try:
		response = s3_client.upload_file(file_name, bucket, object_name)
	except ClientError as e:
		logging.error(e)
		return False
	return True


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
  return render_template('index.jinja.html', msg=request.args.get('msg'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		print(request.files)

		file = request.files['image']

		if file and allowed_file(file.filename):
			uid = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
			filename = secure_filename(file.filename)
			new_name = filename.split('.')[0] + '_' + uid + '.' + filename.split('.')[1]
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))

			upload_file(os.path.join(app.config['UPLOAD_FOLDER'], new_name), 'cloudimageprocessing-zw', object_name=new_name)

			return redirect(url_for('uploaded', filename=filename))
		return redirect(url_for('error', msg='Error with file.'))
	return redirect(url_for('error', msg='Cannot GET /upload'))

@app.route('/uploaded')
def uploaded():
	return 'working'

@app.route('/error')
def error():
	return 'working'

# Disable caching static resources
# Snippet from https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
@app.after_request
def add_header(req):
	req.headers['Pragma'] = 'no-cache'
	req.headers['Expires'] = '0'
	req.headers['Cache-Control'] = 'public, max-age=0'
	return req