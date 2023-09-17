# from flask import Blueprint, jsonify
# from ..config import Config
# from flask_cors import cross_origin

# cursor = Config.cursor
# tab_col = Config.tab_col

# tab_bp = Blueprint("tables", __name__)


# @tab_bp.route("/list", methods=["GET"])
# @cross_origin()
# def get_tables():
#     cursor.execute(
#         "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
#     )
#     tabs = [tab[0] for tab in cursor.fetchall()]
#     return jsonify(tabs)


# @tab_bp.route("/data/<table_name>", methods=["GET"])
# @cross_origin()
# def get_table_data(table_name):
#     cursor.execute(f"SELECT TOP 50 * FROM {table_name}")
#     data = cursor.fetchall()

#     # get column names
#     cursor.execute(
#         f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
#     )
#     cols = [col[0] for col in cursor.fetchall()]

#     # add column names to data
#     data.insert(0, cols)
#     return jsonify(data)


# # todo : deal with dependencies, this doesn't care about those
# @cross_origin()
# @tab_bp.route("/delete/<table_name>", methods=["DELETE"])
# def delete_table(table_name):
#     cursor.execute(f"DROP TABLE {table_name}")
#     tab_col.document(table_name).delete()

#     return jsonify({"message": f"Table {table_name} deleted successfully"})
# from flask import Blueprint, jsonify, request
# from ..config import Config
# from flask_cors import cross_origin

# cursor = Config.cursor
# tab_col = Config.tab_col

# tab_bp = Blueprint("tables", __name__)


# @tab_bp.route("/list", methods=["GET"])
# @cross_origin()
# def get_tables():
#     cursor.execute(
#         "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
#     )
#     tabs = [tab[0] for tab in cursor.fetchall()]
#     return jsonify(tabs)


# @tab_bp.route("/data/<table_name>", methods=["GET"])
# @cross_origin()
# def get_table_data(table_name):
#     cursor.execute(f"SELECT TOP 50 * FROM {table_name}")
#     data = cursor.fetchall()

#     # get column names
#     cursor.execute(
#         f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
#     )
#     cols = [col[0] for col in cursor.fetchall()]

#     # add column names to data
#     data.insert(0, cols)
#     return jsonify(data)


# # todo : deal with dependencies, this doesn't care about those
# @cross_origin()
# @tab_bp.route("/delete/<table_name>", methods=["DELETE"])
# def delete_table(table_name):
#     cursor.execute(f"DROP TABLE {table_name}")
#     tab_col.document(table_name).delete()

#     return jsonify({"message": f"Table {table_name} deleted successfully"})

# @cross_origin()
# @tab_bp.route("/addTable/", methods=["POST"])
# def update_deps():
#     user_input = request.json.get('prompt', None)

#     if user_input is None:
#         return jsonify({"error": "No input provided"}), 400

#     response = call_llm_function(user_input)
#     return jsonify({"table_name": "dummytable", "sql_generated": response})


# def call_llm_function(input):
#     return "SELECT * FROM P_DEMO"


from flask import Blueprint, jsonify, request
from ..config import Config
from flask_cors import cross_origin
from ..ml import llm

cursor = Config.cursor
tab_col = Config.tab_col

tab_bp = Blueprint("tables", __name__)


@tab_bp.route("/list", methods=["GET"])
# @cross_origin()
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


@tab_bp.route("/add", methods=["GET"])
@cross_origin()
def add_table_llm():
    user_input = request.args.get("prompt", None)

    if user_input is None:
        return jsonify({"error": "No input provided"}), 400

    table_name, sql = llm.create_table(user_input)

    return jsonify({"name": table_name, "sql": sql})


@cross_origin()
@tab_bp.route("/test", methods=["POST"])
def post_test():
    return request.json


@cross_origin()
@tab_bp.route("/wtf", methods=["GET"])
def get_test():
    params = request.args
    print(params)
    return jsonify(params)


# from celery import Celery

# celery = Celery("", broker='pyamqp://guest:guest@localhost:5672//')

# @celery.task
# def call_llm_function(input):
#     # your long-running logic here
#     return f"Processed: {input}"

# @tab_bp.route('/llm_status/<task_id>', methods=['GET'])
# def llm_status(task_id):
#     task = call_llm_function.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         response = {
#             'state': task.state,
#             'status': 'Task is still processing'
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'state': task.state,
#             'result': task.result
#         }
#     else:
#         response = {
#             'state': task.state,
#             'status': str(task.info)
#         }
#     return jsonify(response)
