from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from peewee import *
import os, string, random, base64, io
from PIL import Image

# Models
db = 'myresto_fileservice.db'
database = SqliteDatabase(db)
class BaseModel(Model):
	class Meta:
		database = database

class image_file(BaseModel):
	id = AutoField(primary_key=True)
	nama_file = CharField(unique=True)
	link = CharField(unique=True)

def create_tables():
	with database:
		database.create_tables([image_file])


app = Flask(__name__)
api = Api(app)

# config
app.config['imgdir'] = 'static/img/product'

class resource_image_upload(Resource):
	def post(self):
		# parse = reqparse.RequestParser()
		# parse.add_argument('gambar',type=str,help='must str')
		# parse.add_argument('ext',type=str,help='must str')
		# args = parse.parse_args()
		try:
			datas = request.json
			gambar = datas['gambar']
			ext = datas['ext']
			filename = 'restokuimage_'+''.join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for _ in range(10))+"."+ext

			image = base64.b64decode(str(gambar))
			img = Image.open(io.BytesIO(image))

			img.save(filename)


			link = "http://setyawanarik.pythonanywhere.com/static/img/product/"+filename

			image_file.create(
					nama_file=filename,
					link=link
				)

			return jsonify({"hasil":"created","link":link,"filename":"filename",'status':"success"})
		except KeyError:
			return jsonify({"hasil":"Gagal","status":"gagal"})
		except ValueError:
			return jsonify({"hasil":"Gagal","status":"gagal"})

api.add_resource(resource_image_upload, '/api/restokuimage/')

if __name__ == "__main__":
	create_tables()
	app.run()
