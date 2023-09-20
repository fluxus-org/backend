import iris

sql_commands = [
    "SELECT TOP 10 * FROM P_DEMO;",
    "INSERT INTO YourTable (Column1, Column2) VALUES ('Value1', 'Value2');",
    "UPDATE YourTable SET Column1 = 'NewValue' WHERE Condition;",
    "DELETE FROM YourTable WHERE Condition;",
    "ALTER TABLE YourTable ADD COLUMN NewColumn INT;",
    "CREATE TABLE NewTable (Column1 INT, Column2 VARCHAR(255));",
    "DROP TABLE YourTable;",
    "CREATE INDEX IndexName ON YourTable (Column1);",
    "DROP INDEX IndexName;",
    "SELECT * FROM YourTable WHERE Column1 = 'Value';",
    "SELECT Column1, COUNT(*) FROM YourTable GROUP BY Column1;",
    "INSERT INTO TargetTable (Column1, Column2) VALUES ((SELECT Value1 FROM SourceTable), (SELECT Value2 FROM SourceTable));",
    "SAVEPOINT MySavepoint;",
    "SELECT * FROM Customers WHERE EXISTS (SELECT 1 FROM Orders WHERE Customers.CustomerID = Orders.CustomerID);",
    "INSERT INTO Orders (OrderID, CustomerID, Amount) VALUES (101, 1001, 500.00);",
    "SELECT %EXTERNAL(YourValue) AS ExternalValue FROM YourTable;",
    "SELECT %ODBCOUT(YourDate) AS ODBCDate FROM YourTable;",
    "SELECT DATENAME(DAYOFWEEK, YourDate) AS DayName FROM YourTable;",
    "SET NewID = $TSQL_NEWID();",
    "SELECT USER() AS CurrentUser;",
    "SET Element = $LISTGET(MyArray, 2);",
    "DECLARE MyCursor CURSOR FOR SELECT ID, Name FROM YourTable FOR UPDATE;",
    "UPDATE YourTable SET Name = 'NewName' WHERE CURRENT OF MyCursor;",
    "EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM YourTable' INTO @RowCount;",
    "SELECT * FROM YourTable WHERE YourValue %INSET ('Value1', 'Value2', 'Value3');",
    "SELECT * FROM YourTable WHERE YourValue %INLIST ('Value1,Value2,Value3');",
    "SELECT SQRT(25) AS Result;",
    "SET Piece = $PIECE('apple,banana,cherry', ',', 2);",
    "SELECT XMLCONCAT(XMLELEMENT('Name', FirstName), XMLELEMENT('Age', Age)) AS XmlData FROM YourTable;",
    "IF $LISTSAME(Array1, Array2) { WRITE 'Arrays are the same.' }",
    "SELECT TIMESTAMPADD(SQL_TSI_DAY, 7, YourTimestamp) AS NewTimestamp FROM YourTable;",
    "ALTER METHOD YourClass.MethodName() { /* Updated method implementation */ };",
    "CREATE QUERY GetHighValueItems() As %SQLQuery { SELECT Name, Value FROM Inventory WHERE Value > 100; };",
    "DROP QUERY YourClass.GetHighValueItems;",
    "SELECT * FROM YourTable ORDER BY Column1 ASC, Column2 DESC;",
    "EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM YourTable' INTO @RowCount;",
    "SELECT * FROM YourTable WHERE YourColumn %STARTSWITH 'Prefix';",
    "SELECT * FROM YourTable WHERE YourColumn %PATTERN 'A?C*';",
    "SET Element = $LISTGET('apple^banana^cherry', 2);",
    "SELECT TIMESTAMPDIFF(SECOND, Timestamp1, Timestamp2) AS TimeDifference FROM YourTable;",
    "SELECT TO_DATE('2023-09-15', 'YYYY-MM-DD') AS DateValue;",
    "SELECT * FROM YourTable WHERE YourColumn LIKE 'Value%';",
    "SELECT * FROM YourTable WHERE YourColumn NOT LIKE 'Value%';",
    "SELECT * FROM YourTable WHERE YourColumn BETWEEN 100 AND 200;",
    "SELECT * FROM YourTable WHERE YourColumn NOT BETWEEN 100 AND 200;",
    "SELECT * FROM YourTable WHERE YourColumn IS NULL;",
    "SELECT * FROM YourTable WHERE YourColumn IS NOT NULL;",
    "SELECT * FROM YourTable WHERE YourColumn = ANY (SELECT AnotherColumn FROM AnotherTable);",
    "SELECT * FROM YourTable WHERE YourColumn = ALL (SELECT AnotherColumn FROM AnotherTable);",
    "SELECT * FROM YourTable WHERE YourColumn IN (Value1, Value2, Value3);",
    "SELECT * FROM YourTable WHERE YourColumn NOT IN (Value1, Value2, Value3);",
    "SELECT * FROM YourTable WHERE YourColumn = SOME (SELECT AnotherColumn FROM AnotherTable);",
    "SELECT * FROM YourTable WHERE YourColumn = FOR SOME (SELECT AnotherColumn FROM AnotherTable);",
    "SELECT * FROM YourTable WHERE YourColumn = FOR SOME %ELEMENT(%SELECT ID FROM AnotherTable);",
    "SELECT * FROM YourTable WHERE YourColumn = %FIND(%SELECT ID FROM AnotherTable);",
    "SELECT * FROM YourTable WHERE YourColumn = %EXACT('ExactValue');",
    "SELECT * FROM YourTable WHERE YourColumn %MATCHES 'Pattern';",
    "SELECT * FROM YourTable WHERE YourColumn %PATTERN 'Pattern';",
    "SELECT * FROM YourTable WHERE YourColumn %STARTSWITH 'Prefix';",
    "SELECT * FROM YourTable WHERE YourColumn %INLIST(Value1, Value2, Value3);",
    "SELECT * FROM YourTable WHERE YourColumn %INSET(Value1, Value2, Value3);",
    "SELECT * FROM YourTable WHERE YourColumn %INTERNAL(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %EXTERNAL(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %ODBCIN(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %ODBCOUT(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %OBJECT(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %SQLSTRING(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %SQLUPPER(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %JSONNULLIF(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %EXISTS(Value);",
    "SELECT * FROM YourTable WHERE YourColumn %EXISTS(%SELECT ID FROM AnotherTable WHERE AnotherColumn = YourTable.YourColumn);",
    "SELECT * FROM YourTable WHERE YourColumn %ISNULL(Value);"
]

# Define the database connection parameters
server = "server"
namespace = "namespace"
username = "user"
password = "password"
port = 8000  # Your database port

conn_string = f"{server}:{port}/{namespace}"
conn = iris.connect(conn_string, username, password)

cursor = conn.cursor()

# Execute SQL commands
for sql_command in sql_commands:
    try:
        cursor.execute(sql_command)
        result = cursor.fetchall()
        print(f"Query Result: {result}")
    except Exception as e:
        print(f"Error executing SQL command: {e}")

# Close the cursor and connection
cursor.close()
conn.close()
