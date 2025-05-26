import pandas as pd
from sqlalchemy import create_engine
import configparser

# Read the properties file
config = configparser.ConfigParser()
config.read('msg.properties')

# Extract the relevant column mapping
msg_id = config['Transaction_Pacs8_Outwards']['tx_pacs8out_Message_id']

# Create a connection to the database
pd.set_option('display.max_columns', None)
cnx = create_engine('sqlite:///payments.db').connect()

# Use the mapped column in the SQL query
query_outwards = f"""
SELECT *
FROM Transaction_Pacs8_Outwards
WHERE {msg_id} = '1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g';
"""

# Execute the query and load the data into a pandas DataFrame
data_outwards = pd.read_sql_query(query_outwards, cnx)

# Display the result
print(data_outwards)
