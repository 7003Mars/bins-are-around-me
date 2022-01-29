import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional, cast

from flask import Flask
from flask import json as flask_json
from flask import jsonify, request
from flask_cors import CORS  # TODO: Needed?
from flask_restx import Api, Resource
from flask_restx.reqparse import RequestParser
from flask_socketio import SocketIO as SocketIO_Flask
from flask_sqlalchemy import SQLAlchemy
from geopy.geocoders import Nominatim
from typing_extensions import TypedDict

app: Flask = Flask(__name__)
CORS(app)
# Sockets
socket: SocketIO_Flask = SocketIO_Flask(app, cors_allowed_origins="*", json=flask_json)
# Rest
api: Api = Api(app)
# Db config
db_path: str = 'sqlite:///' + str(Path(__file__).parent.resolve() / "database.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
db: SQLAlchemy = SQLAlchemy(app)
# Db models


class Bins(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    last_update = db.Column(db.DateTime, default=datetime.now)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    state = db.Column(db.Enum('EMPTY', 'FULL'))
    addr = db.Column(db.String(255))


Bin = TypedDict('Bin', {'id': int, 'last_update': datetime, 'lat': float, 'lng': float, 'state': str, 'addr': str})

# Others
id_socket_link: dict[str, str] = dict()


def all_bins() -> list[Bin]:
    cols: list[str] = Bins.query.first().__table__.columns.keys()
    return cast(list[bin], [{col: getattr(bin_, col) for col in cols} for bin_ in Bins.query.all()])  # Hope nothing goes wrong if I miscast


def json_serial(obj):  # Stolen from https://stackoverflow.com/a/22238613
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# Sockets
@socket.on('connect')  # TODO: /api/ route for apis
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
@api.route('/api/add-bin')
class AddBin(Resource):
    def post(self):
        parser: RequestParser = RequestParser()
        parser.add_argument('lat', type=float, required=True)
        parser.add_argument('lng', type=float, required=True)
        result: dict = parser.parse_args()

        lat: float = result['lat']
        lng: float = result['lng']
        full_addr: str = Nominatim(user_agent='6bceb638-f132-4961-b7c2-fe6d588df78d').reverse((lat, lng)).address
        addr: str = ','.join(full_addr.split(',', 2)[0:2])
        bins: Bins = Bins(lat=lat, lng=lng, state='EMPTY', addr=addr)
        db.session.add(bins)
        db.session.commit()
        socket.emit('new-bin', {'id': bins.id_, 'lat': lat, 'lng': lng, 'addr': addr, 'state': 'EMPTY'})
        return jsonify(bins.id_)


@api.route('/api/get-bins')
class ListBins(Resource):
    def get(self):
        result: list[Bin] = all_bins()
        logging.info(result)
        return jsonify(result)


@api.route('/api/test-ping')
class TestPing(Resource):
    def get(self):
        state: str = request.json['state']
        socket.emit('bin-update', {'id_': 1, 'state': state.upper()})

        # socket.emit('test-ping', {'message': 'pong'})
        return


if __name__ == '__main__':
    app.run(debug=True)
