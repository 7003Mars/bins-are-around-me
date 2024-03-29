import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Optional, cast

from flask import Blueprint, Flask, abort
from flask import json as flask_json
from flask import jsonify, render_template, request
from flask_cors import CORS  # TODO: Needed?
from flask_restx import Api, Resource
from flask_restx.reqparse import RequestParser
from flask_socketio import SocketIO as SocketIO_Flask
from flask_sqlalchemy import SQLAlchemy
from geopy.geocoders import Nominatim
from PIL import Image
from typing_extensions import TypedDict
from werkzeug.datastructures import FileStorage

from classifier import States, get_state_result

app: Flask = Flask(__name__, static_url_path='', static_folder='frontend/dist')
CORS(app)
# Sockets
socket: SocketIO_Flask = SocketIO_Flask(
    app, cors_allowed_origins='*', json=flask_json)
# Rest
api_bp: Blueprint = Blueprint('api', __name__)
api: Api = Api(api_bp)
# Db config
db_path: str = 'sqlite:///' + \
    str(Path(__file__).parent.resolve() / "database.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
db: SQLAlchemy = SQLAlchemy(app)
# Db models


class Bins(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    last_update = db.Column(db.DateTime, default=datetime.now)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    state = db.Column(db.Enum('EMPTY', 'FULL', 'OVERFLOW'))
    addr = db.Column(db.String(255))


Bin = TypedDict('Bin', {'id': int, 'last_update': datetime,
                'lat': float, 'lng': float, 'state': str, 'addr': str})
# Multithreading
pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=2)


def state_future_wrapper(bin_id: int) -> Callable[..., None]:
    def wrapper(*args, **kwargs):
        res = get_state_result(*args, **kwargs)
        row = Bins.query.get(bin_id)  # TODO: Type
        if row is None:
            return
        row.state = res.name
        db.session.commit()
        socket.emit('bin-update', {'id_': bin_id, 'state': res.name})
        print(f'Bin {bin_id} updated to {res}')
    return wrapper


# Others
id_socket_link: dict[str, str] = dict()


def all_bins() -> list[Bin]:
    cols: list[str] = Bins.query.first().__table__.columns.keys()
    # Hope nothing goes wrong if I miscast
    return cast(list[Bin], [{col: getattr(bin_, col) for col in cols} for bin_ in Bins.query.all()])


def json_serial(obj):  # Stolen from https://stackoverflow.com/a/22238613
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# Sockets
@socket.on('connect')
def connect(auth: dict) -> Optional[bool]:
    sid: str = request.sid  # type:ignore
    socket.emit('bins', all_bins(), room=sid)
    if not auth or 'id' not in auth:
        return None
    id_: str = auth['id']
    if Bins.query.get(id_).first():
        return bool(id_socket_link.setdefault(sid, id_))
        # return id_set
    return None


# Api
@api.route('/add-bin')
class AddBin(Resource):
    parser: RequestParser = RequestParser()
    parser.add_argument('lat', type=float, required=True)
    parser.add_argument('lng', type=float, required=True)

    @api.expect(parser)
    def post(self):
        result: dict = type(self).parser.parse_args()

        lat: float = result['lat']
        lng: float = result['lng']
        full_addr: str = Nominatim(
            user_agent='6bceb638-f132-4961-b7c2-fe6d588df78d').reverse((lat, lng)).address
        addr: str = ','.join(full_addr.split(',')[0:3])
        bins: Bins = Bins(lat=lat, lng=lng, state='EMPTY', addr=addr)
        db.session.add(bins)
        db.session.commit()
        socket.emit('new-bin', {'id': bins.id_, 'lat': lat,
                    'lng': lng, 'addr': addr, 'state': 'EMPTY'})
        return jsonify(bins.id_)


@api.route('/get-bins')
class ListBins(Resource):
    def get(self):
        result: list[Bin] = all_bins()
        logging.info(result)
        return jsonify(result)


@api.route('/change-state')
class TestPing(Resource):
    # This is only here for the swagger docs
    parser: RequestParser = RequestParser()
    parser.add_argument('id', type=int, required=True)
    parser.add_argument('state', type=str, required=True,
                        choices=States._member_names_)

    @api.expect(parser)
    def post(self):
        # TODO: I'm sure there is a better way to get the parser
        result: dict = type(self).parser.parse_args()
        id_: int = result['id']
        state: str = result['state'].upper()
        row = Bins.query.get(id_)  # TODO: Type
        if row is not None:
            row.state = state
        else:
            # TODO: This might be the wrong errror code
            return abort(400, f'Bin {id_} does not exist')
        db.session.commit()
        socket.emit('bin-update', {'id_': id_, 'state': state})
        # socket.emit('test-ping', {'message': 'pong'})
        return


# @api.route('/test-file')
# class TestFile(Resource):
#     def get(self):
#         file_path: str = Path(__file__).parent.resolve() / \
#             'img' / request.json['file_path']
#         pool.submit(state_future_wrapper(1), path=file_path)
#         return


@api.route('/update-bin')
class UpdateBin(Resource):
    parser: RequestParser = RequestParser()
    parser.add_argument('id', type=int, required=True, location='form')
    parser.add_argument('file', type=FileStorage,
                        location='files', required=True)

    @api.expect(parser)
    def post(self):
        result: dict = type(self).parser.parse_args()
        id_: int = result['id']
        file = result['file']
        image: Image.Image = Image.open(file)
        image.load()
        pool.submit(state_future_wrapper(id_), image=image)
        return


# Bin report
# TODO: Make it a vue page
@app.get('/bin-report')
def bin_report():
    return render_template('bin-report.html')


app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
    # res = pool.submit(future_wrapper(1), path='./img/1.jpg')
    # time.sleep(5)
    # res = pool.submit(future_wrapper(1), path='./img/2.jpg')

    # while not res.done():
    #     time.sleep(0.2)
