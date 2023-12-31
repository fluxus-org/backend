from flask import Blueprint, jsonify, request

from flask_cors import cross_origin

from pandas.core import methods
from ..config import Config

cursor = Config.cursor
tab_col = Config.tab_col

dep_bp = Blueprint("deps", __name__)


# @dep_bp.route("/list/<table_name>", methods=["GET"])
# def get_deps(table_name):
#     tab_deps = tab_col.document(table_name).get().to_dict().get("deps", [])
#     return jsonify(tab_deps)


@dep_bp.route("/list/", methods=["GET"])
@cross_origin()
def get_deps():
    docs = tab_col.stream()
    all_deps = {}

    for doc in docs:
        all_deps[doc.id] = doc.to_dict().get("deps", [])

    return jsonify(all_deps)


@dep_bp.route("/update/<table_name>/", methods=["POST"])
@cross_origin()
def update_deps(table_name):
    deps = request.json.get("deps", [])
    tab_col.document(table_name).update({"deps": deps})
    return jsonify({"message": "Dependencies updated successfully"})
