


import pandas as pd
from sqlalchemy import create_engine


pd.set_option('display.max_columns', None)
# Create a connection to the database
cnx = create_engine('sqlite:///payments.db').connect()

# Query the table to retrieve data where BizMsgIdr matches
query = """
SELECT *
FROM Transaction_Pacs8_Inwards
WHERE BizMsgIdr = '1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g';
"""


# Execute the query and load the data into a pandas DataFrame\




data = pd.read_sql_query(query, cnx)

# Display the retrieved data
print(data)
