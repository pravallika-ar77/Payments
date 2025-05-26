import pandas as pd
from sqlalchemy import create_engine

#display columns
pd.set_option('display.max_columns', None)


#connection to the database
cnx = create_engine('sqlite:///payments.db').connect()

# Query
query_return = """
SELECT *
FROM Message_Pacs4
WHERE BizMsgIdr = '1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g';
"""


data_return = pd.read_sql_query(query_return, cnx)


print(data_return)