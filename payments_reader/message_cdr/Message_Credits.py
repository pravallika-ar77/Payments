import pandas as pd
from sqlalchemy import create_engine

# display  all columns
pd.set_option('display.max_columns', None)


#connection to the database
cnx = create_engine('sqlite:///payments.db').connect()

# Query the table to retrieve data where BizMsgIdr matches
query = """
SELECT *
FROM Message_Pacs8_Inward
WHERE BizMsgIdr = '19K8gzrzNLm6w6eohmJ2xyKnNyFDiPDWQz';
"""



data = pd.read_sql_query(query, cnx)


print(data)
