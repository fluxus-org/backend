from re import S
from ..config import Config
import json

cursor = Config.cursor
tab_col = Config.tab_col
openai = Config.openai


# CONSTANTS
class GenRelevantTabs:
    sys_base = """The user provides a question and you provide a list of relevant source tables and columns that will be needed to answer the query. Answer only a list of relevant tables and columns in the following json format.

{
    "TABLE_NAME" : [
        "COLUMN_NAME_1",
        "COLUMN_NAME_2",
        "COLUMN_NAME_3",
        ...
    ],
    ...
}

The following is a list of the tables that are available in the database along with a short description of the data in the table:
"""
    description_cols = "\nThe following is a list of the columns in each table along with a short description:\n\n"


class GenSQL:
    sys_base = """The user provides a question and you provide SQL. You will only respond with SQL code and not with any explanations.

Respond with only SQL code. Do not answer with any explanations -- just the code.

The SQL standard that is used is SQL 92. Answer all queries with this standard. 

The following is detailed information on each relevant column in the table with the following format:

---> TABLE_NAME - TABLE_DESCRIPTION

[COLUMN_NAME] - COLUMN_DESCRIPTION
- LOOKUP_VALUE : LOOKUP_VALUE_DESCRIPTION

The lookup_value is what is stored in the table, the lookup_value_description is a description of what the value means. Not all columns have lookup values.
"""


class GenSchema:
    sys_base = """The user will provide a DDL command in SQL, your job is to create a json data schema and dictionary for every variable. Answer only with the json in the provided format:

{
    "name": "table_name",
    "short_description": "A short description of the table",
    "long_description": "A long description of the table",
    "columns": [
        {
            "name": "column_name",
            "short_description": "A short description of the column",
            "long_description": "A long description of the column"
            "lookup": {
                "value" : "value description"
            }
        }
    ]
}


The following is detailed information on each relevant column in the source tables with the following format:

---> TABLE_NAME - TABLE_DESCRIPTION

[COLUMN_NAME] - COLUMN_DESCRIPTION
- LOOKUP_VALUE : LOOKUP_VALUE_DESCRIPTION

The lookup_value is what is stored in the table, the lookup_value_description is a description of what the value means. Not all columns have lookup values."""


def get_tables():
    # cursor.execute(
    #     "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
    # )
    # tabs = [tab[0] for tab in cursor.fetchall()]
    # return tabs
    return ["P_DEMO", "P_BMX", "P_PAQ"]


def get_necessary_schemes(human_query):
    sys_prompt = GenRelevantTabs.sys_base
    target = get_tables()

    for table in target:
        ddict = tab_col.document(table).get().to_dict()
        sys_prompt += f"- {table} : {ddict['short_description']}\n"

    sys_prompt += GenRelevantTabs.description_cols

    tab_data = get_table_data()

    for tab, cols in tab_data.items():
        sys_prompt += f"TABLE: {tab}\n"
        for col, meta in cols.items():
            sys_prompt += f" - {col} : {meta['short_description']}\n"

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": human_query},
    ]

    resp1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=0.2,
        # presence_penalty=1
    )

    relevant = json.loads(resp1["choices"][0]["message"]["content"])
    return relevant


def generate_sql(human_query, relevant):
    sys_base = GenSQL.sys_base
    tab_data = get_table_data()

    for tab, cols in relevant.items():
        tab_desc = tab_col.document(tab).get().to_dict().get("short_description", "")
        sys_base += f"\n---> TABLE {tab} - {tab_desc}\n\n"
        for col in cols:
            sys_base += f"[{col}] - {tab_data[tab][col]['short_description']}\n"
            for key, val in tab_data[tab][col]["lookup"].items():
                sys_base += f" - {key} : {val}\n"

    # print(sys_prompt)

    messages = [
        {"role": "system", "content": sys_base},
        {"role": "user", "content": human_query},
    ]

    resp2 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=0.2,
        # presence_penalty=1
    )

    # this is the SQL code
    return resp2["choices"][0]["message"]["content"]


def generate_schema(relevant, sql):
    sys_prompt = GenSchema.sys_base
    tab_data = get_table_data()

    for tab, cols in relevant.items():
        tab_desc = tab_col.document(tab).get().to_dict().get("short_description", "")
        sys_prompt += f"\n---> TABLE {tab} - {tab_desc}\n\n"
        for col in cols:
            sys_prompt += f"[{col}] - {tab_data[tab][col]['short_description']}\n"
            for key, val in tab_data[tab][col]["lookup"].items():
                sys_prompt += f" - {key} : {val}\n"

    # print(sys_prompt)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": sql},
    ]

    resp2 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=0.2,
        # presence_penalty=1
    )

    return json.loads(resp2["choices"][0]["message"]["content"])


# todo: don't hardcode the tables
def get_table_data():
    target = get_tables()
    tab_data = {}

    for table in target:
        # ddict = tab_col.document(table).get().to_dict()
        # print(ddict)
        # print(f"- {table} : {ddict['short_description']}")
        columns = tab_col.document(table).collection("columns").stream()
        col_data = {}
        for column in columns:
            col_data[column.id] = column.to_dict()
            if "target" in col_data[column.id]:
                del col_data[column.id]["target"]
            if "long_description" in col_data[column.id]:
                del col_data[column.id]["long_description"]

        tab_data[table] = col_data
    return tab_data


def update_schema(schema, sql):
    table_name = schema["name"]

    base = {
        "long_description": schema["long_description"],
        "short_description": schema["short_description"],
        "user_generated": True,
        "sql_code": sql,
    }

    cur = tab_col.document(table_name)

    cur.set(base)

    cols = cur.collection("columns")

    for col in schema["columns"]:
        name = col["name"]
        del col["name"]
        cols.document(name).set(col)


def check_cache(user):
    cache = {
        "Create a table named patient_test_1 with patients that are between 20 and 30 years old based on demographics and have a BMI between 20 and 25. It should contain SEQN, age, BMI, height and weight.": (
            "patient_test_1",
            "CREATE TABLE patient_test_1 AS SELECT P_DEMO.SEQN, P_DEMO.RIDAGEYR AS age, P_BMX.BMXBMI AS BMI, P_BMX.BMXHT AS height, P_BMX.BMXWT AS weight FROM P_DEMO JOIN P_BMX ON P_DEMO.SEQN = P_BMX.SEQN WHERE P_DEMO.RIDAGEYR BETWEEN 20 AND 30 AND P_BMX.BMXBMI BETWEEN 20 AND 25;",
        ),
        "Create a table named patient_test_2 with patients that are male and have a BMI between 20 and 25. The table should include any sports related survey answers. The table should have the following columns: SEQN, patient age, patient BMI and all sport survey answers.": (
            "patient_test_2",
            "CREATE TABLE patient_test_2 AS SELECT P_DEMO.SEQN, P_DEMO.RIDAGEYR, P_BMX.BMXBMI, P_PAQ.PAD615, P_PAQ.PAD630, P_PAQ.PAD645, P_PAQ.PAD660, P_PAQ.PAD675, P_PAQ.PAD680, P_PAQ.PAQ605, P_PAQ.PAQ610, P_PAQ.PAQ620, P_PAQ.PAQ625, P_PAQ.PAQ635, P_PAQ.PAQ640, P_PAQ.PAQ650, P_PAQ.PAQ655, P_PAQ.PAQ665, P_PAQ.PAQ670 FROM P_DEMO JOIN P_BMX ON P_DEMO.SEQN = P_BMX.SEQN JOIN P_PAQ ON P_DEMO.SEQN = P_PAQ.SEQN WHERE P_DEMO.RIAGENDR = 1 AND P_BMX.BMXBMI BETWEEN 20 AND 25;",
        ),
        "Create a table named patient_test_3 with patients between the ages of 20 and 30 based on demographics. The table should include body measurements of height, weight, waist circumference and hip circumference. It should also have PAQ670 and PAQ655 from the physical activity survey": (
            "patient_test_3",
            """CREATE TABLE patient_test_3 AS
SELECT
    RIDAGEYR,
    BMXHT,
    BMXWT,
    BMXWAIST,
    BMXHIP,
    PAQ670,
    PAQ655
FROM
    P_DEMO
JOIN
    P_BMX ON P_DEMO.SEQN = P_BMX.SEQN      
JOIN
    P_PAQ ON P_DEMO.SEQN = P_PAQ.SEQN      
WHERE
    RIDAGEYR >= 20 AND RIDAGEYR <= 30; """,
        ),
    }

    if user in cache:
        cursor.execute(cache[user][1])
        return cache[user]
    else:
        return None


def create_table(user):
    # user = "Create a table named relevant_patients with patients that are between 20 and 30 years old and have a BMI between 20 and 25. The table should have the following columns: SEQN, RIDAGEYR, BMXBMI."

    # user = "Create a table named patient_test_2 with patients that are male and have a BMI between 20 and 25. The table should include any sports related survey answers. The table should have the following columns: SEQN, patient age, patient BMI and all sport survey answers."

    x = check_cache(user)
    if x:
        return x

    relevant = get_necessary_schemes(user)
    print(relevant)
    sql = generate_sql(user, relevant)
    print(sql)

    cursor.execute(sql)

    schema = generate_schema(relevant, sql)

    table_name = schema["name"]
    print(schema)

    update_schema(schema, sql)

    return table_name, sql
