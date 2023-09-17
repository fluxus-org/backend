from flask import Blueprint, jsonify
from ..config import Config
from flask_cors import cross_origin

cursor = Config.cursor
tab_col = Config.tab_col

tab_bp = Blueprint("tables", __name__)


@tab_bp.route("/list", methods=["GET"])
@cross_origin()
def get_tables():
    cursor.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
    )
    tabs = [tab[0] for tab in cursor.fetchall()]
    return jsonify(tabs)


@tab_bp.route("/data/<table_name>", methods=["GET"])
@cross_origin()
def get_table_data(table_name):
    cursor.execute(f"SELECT TOP 50 * FROM {table_name}")
    data = cursor.fetchall()

    # get column names
    cursor.execute(
        f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
    )
    cols = [col[0] for col in cursor.fetchall()]

    # add column names to data
    data.insert(0, cols)
    return jsonify(data)


# todo : deal with dependencies, this doesn't care about those
@cross_origin()
@tab_bp.route("/delete/<table_name>", methods=["DELETE"])
def delete_table(table_name):
    cursor.execute(f"DROP TABLE {table_name}")
    tab_col.document(table_name).delete()

    return jsonify({"message": f"Table {table_name} deleted successfully"})
