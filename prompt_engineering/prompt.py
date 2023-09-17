import os
import openai
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

schema_dict = {}

def get_all_schemas():
  cred = credentials.Certificate("fluxus-cd802-firebase-adminsdk-77hzw-44c6ecda5b.json")
  firebase_admin.initialize_app(cred)

  db = firestore.client()
  tables = db.collection('tables').stream()

  for table in tables:
    table_dict = table.to_dict()
    columns = table.reference.collection(u"columns").stream()
    col_data = {}
    for column in columns:
      col_data[column.id] = column.to_dict()
      if ("target" in col_data[column.id]):
        del col_data[column.id]["target"]
      if ("long_description" in col_data[column.id]):
        del col_data[column.id]["long_description"]
    table_dict["columns"] = col_data
    schema_dict[table.id] = table_dict
  
  with open('result.json', 'w') as fp:
    json.dump(schema_dict, fp)

def get_necessary_schemes(human_query):
  """Get the necessary schemas for the SQL command."""
  tables_and_cols_only = {}
  for table in schema_dict:
    tables_and_cols_only[table] = {}
    for field in schema_dict[table]:
      if field == "short_description":
        tables_and_cols_only[table][field] = schema_dict[table][field]
      elif field == "columns":
        tables_and_cols_only[table][field] = {}
        for col in schema_dict[table][field]:
          tables_and_cols_only[table][field][col] = {}
          for item in schema_dict[table][field][col]:
            if item == "short_description" or item == "lookup":
              tables_and_cols_only[table][field][col][item] = schema_dict[table][field][col][item]

  messages = [
      {
          "role": "system",
          "content": "You are a SQL code translator. Your role is to translate natural language to PostgreSQL. I will only pass in data tables, their short descriptions, columns they have, and description of the columns. I need you to identify the tables you need. Return it as an array of strings for table names. Ex. ['table1', 'table2'] and nothing else."
      },
      {
          "role": "user",
          "content": f"Predict which tables we will need to turn \"{human_query}\" to a syntactically-correct PostgreSQL query. Return as a JSON. Here is the schema you can pick out from \"{tables_and_cols_only}\". Do not include anything else in the response but the array of table names."
      }
  ]
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",
      messages=messages
  )
  print("JSON Response is ", response)

  return response

def human_text_to_sql(query, needed_schemes):
  """Convert a human-readable text to SQL using OpenAI API."""
  query_tables = {}
  for table in schema_dict:
    if table in needed_schemes.toArray():
      query_tables[table] = schema_dict[table]
      print("\n\nTable name : %s \n"% (table))
  print("AFTER ALL ", query_tables)
  messages = [
      {
          "role": "system",
          "content": "You are a SQL code translator. Your role is to translate natural language to PostgreSQL. Your only output should be SQL code. Do not include any other text. Only SQL code. Use the database schemas properly to identify the encoding and correct look up values."
      },
      {
          "role": "user",
          "content": f"Translate \"{query}\" to a syntactically-correct PostgreSQL query. Here are the schemas for all our databases \"{query_tables}\". "
      }
  ]

  response = openai.ChatCompletion.create(  # This line may vary based on the latest OpenAI SDK
      model="gpt-3.5-turbo-16k",
      messages=messages
  )

  return response['choices'][0]['message']['content']

def testSql(sql_command):
  """Test if the SQL command is valid."""
  return True

# def update_schemas(sql_command):
#   """Update the schema_dict with the new SQL command."""
  
#   response = openai.Completion.create(
#     engine="gpt-3.5-turbo ",
#     prompt=f""""You are a SQL code translator. Your role is to translate natural language to PostgreSQL. Your only output should be SQL code. Do not include any other text. Only SQL code. 
#     Translate \"{query}\" to a syntactically-correct PostgreSQL query. Here are the schemas for all our databases \"{schema_dict}\"""",
#     max_tokens=50
#   )

#   # Extract the SQL command from the response
#   sql_command = response.choices[0].text.strip()
#   print("Response is ", response)
#   return sql_command

if __name__ == "__main__":
  get_all_schemas();
  human_query = input("Enter your English sentence: ")

  needed_schemes = get_necessary_schemes(human_query)

  print("NEEDED SCHEMES ARE ", needed_schemes)
  print("HUMAN QUERY IS ", human_query)
  sql_result = human_text_to_sql(human_query, needed_schemes)
  print (sql_result)
  fail_count = 0
  while testSql(sql_result) == False and fail_count < 3:
    sql_result = human_text_to_sql(human_query)
    fail_count += 1
  
  if fail_count > 3:
    print("Failed to generate SQL command.")
  else:
    print("Generated SQL Command:", sql_result, "\n")