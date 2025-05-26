import pandas as pd
from sqlalchemy import create_engine

# Display all columns in output
pd.set_option('display.max_columns', None)

# Connect to the SQLite database
cnx = create_engine('sqlite:///payments.db').connect()

# Query for Transaction_Pacs4
query_transaction = """
SELECT *
FROM Transaction_Pacs4
WHERE BizMsgIdr = '1FvkQzPSFmdFGygNbHaGFutobJs3HUwU57';
"""

# Execute the query and store the result in a DataFrame
data_transaction = pd.read_sql_query(query_transaction, cnx)

# Print the result
print(data_transaction)
