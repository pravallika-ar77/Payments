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
query_summary = f"""
SELECT DbtrAgt, COUNT(*) AS transactions, SUM(RtrdIntrBkSttlmAmt) AS total_amount
FROM Transaction_Pacs4
WHERE DbtrAgt LIKE '{bank_prefix}%'
GROUP BY DbtrAgt
ORDER BY DbtrAgt;
"""

# Load the data from the database
summary_data = pd.read_sql_query(query_summary, cnx)

# Close the connection
cnx.close()

# Calculate total values
total_transactions = summary_data['transactions'].sum()
total_amount = summary_data['total_amount'].sum()

# Create a DataFrame for the totals in column format
total_data = pd.DataFrame({
    'DbtrAgt': ['Total'],
    'transactions': [total_transactions],
    'total_amount': [total_amount]
})

# Display results for the selected bank prefix
st.write(f"### Summary for Bank Prefix: {bank_prefix}")
st.dataframe(summary_data, use_container_width=True)  # Display the summary data as a table

# Display the total as a separate row below the table
st.write("### Total ")
st.dataframe(total_data, use_container_width=True)  # Display the total in a column-like format
