from flask_smorest import abort, Blueprint
from flask.views import MethodView
from db import db
from sqlalchemy.exc import SQLAlchemyError
from models import WoodModel
from schema import WoodSchema


blp = Blueprint('DataWood', 'wood', description='Operations on the wood')


@blp.route('/wood')
class WoodList(MethodView):

    @blp.response(200, WoodSchema(many=True))
    def get(self):
        wood = WoodModel.query.all()
        return wood

    @blp.arguments(WoodSchema)
    @blp.response(201, WoodSchema)
    def post(self, parsed_data):
        wood = WoodModel(**parsed_data)
        try:
            db.session.add(wood)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return wood


@blp.route('/wood/<int:wood_id>')
class Wood(MethodView):

    @blp.response(200, WoodSchema)
    def get(self, wood_id):
        wood = WoodModel.query.get_or_404(wood_id)
        return wood

    @blp.response(200, WoodSchema)
    def delete(self, wood_id):
        wood = WoodModel.query.get_or_404(wood_id)
        db.session.delete(wood)
        db.session.commit()
        return {
            "message": "wood deleted from database."
        }
