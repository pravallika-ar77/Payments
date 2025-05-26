import pandas as pd
from sqlalchemy import create_engine

pd.set_option('display.max_columns', None)

# Create a connection to the database
cnx = create_engine('sqlite:///payments.db').connect()

# Query the table to retrieve data where BizMsgIdr matches for the Outwards table
query_outwards = """
SELECT *
FROM Transaction_Pacs8_Outwards
WHERE BizMsgIdr = '1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g';
"""

# Execute the query and load the data into a pandas DataFrame for Outwards
data_outwards = pd.read_sql_query(query_outwards, cnx)

# Display the retrieved data for Outwards
print(data_outwards)
