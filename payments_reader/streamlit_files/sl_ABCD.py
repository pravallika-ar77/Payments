import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Streamlit app title
st.title("Agent Transactions Summary")

# Dropdown to select the bank prefix
bank_prefix = st.selectbox(
    "Select Bank Prefix",
    options=["ABNK", "BBNK", "CBNK", "DBNK"]
)

# Connect to the database
cnx = create_engine('sqlite:///payments.db').connect()

# SQL queries with dynamic bank prefix
credited_query = f"""
SELECT CdtrAgt, COUNT(*) AS credited_transactions, SUM(IntrBkSttlmAmt) AS credited_amount
FROM Transaction_Pacs8_Inwards
WHERE CdtrAgt LIKE '{bank_prefix}%'
GROUP BY CdtrAgt
"""

debited_query = f"""
SELECT DbtrAgt, COUNT(*) AS debited_transactions, SUM(IntrBkSttlmAmt) AS debited_amount
FROM Transaction_Pacs8_Outwards
WHERE DbtrAgt LIKE '{bank_prefix}%'
GROUP BY DbtrAgt
"""

# Load the data from the database
credited_data = pd.read_sql_query(credited_query, cnx)
debited_data = pd.read_sql_query(debited_query, cnx)

# Close the connection
cnx.close()

# Rename columns for consistency
credited_data.rename(columns={
    'CdtrAgt': 'Agt',
    'credited_transactions': 'transactions_C',
    'credited_amount': 'amount_C'
}, inplace=True)

debited_data.rename(columns={
    'DbtrAgt': 'Agt',
    'debited_transactions': 'transactions_D',
    'debited_amount': 'amount_D'
}, inplace=True)

# Merge the credited and debited data
merged_data = pd.merge(credited_data, debited_data, on='Agt', how='left')

# Fill missing values with 0
merged_data['amount_D'] = merged_data['amount_D'].fillna(0)
merged_data['transactions_D'] = merged_data['transactions_D'].fillna(0)

# Calculate total balance
merged_data['total_balance'] = merged_data['amount_C'] - merged_data['amount_D']

# Create a total row
total_row = pd.DataFrame([{
    'Agt': 'TOTAL',
    'transactions_C': merged_data['transactions_C'].sum(),
    'amount_C': merged_data['amount_C'].sum(),
    'transactions_D': merged_data['transactions_D'].sum(),
    'amount_D': merged_data['amount_D'].sum(),
    'total_balance': merged_data['total_balance'].sum()
}])

# Append total row to the bottom of the DataFrame
merged_data_with_total = pd.concat([merged_data, total_row], ignore_index=True)

# Display results
st.write(f"### Transactions for Bank Prefix: {bank_prefix}")
st.dataframe(merged_data_with_total)
