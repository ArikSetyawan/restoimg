from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from peewee import *
import os, string, random, base64, io
from PIL import Image

# Models
import urllib.parse

db_proxy = Proxy()



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

if 'HEROKU' in os.environ:
    import urlparse, psycopg2
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    db = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
    db_proxy.initialize(db)
else:
    db = SqliteDatabase('persons.db')
    db_proxy.initialize(db)

app = Flask(__name__)
api = Api(app)

# config
app.config['imgdir'] = 'static/img/product'

@app.before_request
def before_request():
    g.db = db_proxy
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

class index(Resource):
	def get(self):
		datas = image_file.select()
		data_image = []
		if datas.exists():
			for i in datas:
				data = {}
				data['id'] = i.id
				data['nama_file'] = i.nama_file
				data['link'] = i.link
				data_image.append(data)
			return jsonify({"hasil":data_image,"status":"success"})
		else:
			return jsonify({"hasil":data_image,"status":"gagal"})

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

			img.save(os.path.join(app.config['imgdir'],filename))


			link = "https://restoimg.herokuapp.com/static/img/product/{}".format(filename)

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
api.add_resource(index,'/')

if __name__ == "__main__":
	db_proxy.connect()
	create_tables()
	app.run()
