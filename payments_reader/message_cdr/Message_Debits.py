import pandas as pd
from sqlalchemy import create_engine

#display columns
pd.set_option('display.max_columns', None)


#connection to the database
cnx = create_engine('sqlite:///payments.db').connect()

# Query
query_outward = """
SELECT *
FROM Message_Pacs8_Outward
WHERE BizMsgIdr = '1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g';
"""


data_outward = pd.read_sql_query(query_outward, cnx)


print(data_outward)
