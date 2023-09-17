import openai
import firebase_admin
from firebase_admin import credentials, firestore

schema_dict = {}
openai.api_key = "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"

def getSchemaFromFirebase():
  cred = credentials.Certificate("fluxus-cd802-firebase-adminsdk-77hzw-44c6ecda5b.json")
  firebase_admin.initialize_app(cred)

  db = firestore.client()
  tables = db.collection('tables').stream()

  for table in tables:
    table_dict = table.to_dict()
    columns = table.reference.collection(u"columns").stream()
    col_data = []
    for column in columns:
      col_dict = column.to_dict()
      col_data.append(col_dict)
    table_dict["columns"] = col_data
    schema_dict[table.id] = table_dict
  
def human_text_to_sql(query):
  """Convert a human-readable text to SQL using OpenAI API."""
  print("Your query is ", query)
  response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=f""""You are a SQL code translator. Your role is to translate natural language to PostgreSQL. Your only output should be SQL code. Do not include any other text. Only SQL code. 
    Translate \"{query}\" to a syntactically-correct PostgreSQL query. Here are the schemas for all our databases \"{schema_dict}\"""",
    max_tokens=50
  )

  # Extract the SQL command from the response
  sql_command = response.choices[0].text.strip()
  print("Response is ", response)
  return sql_command

if __name__ == "__main__":
  getSchemaFromFirebase();
  human_query = input("Enter your English sentence: ")
  sql_result = human_text_to_sql(human_query)
  print(f"SQL command: {sql_result}")