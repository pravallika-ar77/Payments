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

# ---------- Section 1: Credit and Debit Transactions Summary ----------

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

credited_data = pd.read_sql_query(credited_query, cnx)
debited_data = pd.read_sql_query(debited_query, cnx)

# Rename columns
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

# Merge credited and debited data
merged_cd_data = pd.merge(credited_data, debited_data, on='Agt', how='outer')
merged_cd_data[['amount_C', 'transactions_C', 'amount_D', 'transactions_D']] = \
    merged_cd_data[['amount_C', 'transactions_C', 'amount_D', 'transactions_D']].fillna(0)

# ---------- Section 2: Returned Transactions Summary (Pacs4) ----------

returned_query = f"""
SELECT DbtrAgt AS Agt, COUNT(*) AS transactions_R, SUM(RtrdIntrBkSttlmAmt) AS amount_R
FROM Transaction_Pacs4
WHERE DbtrAgt LIKE '{bank_prefix}%'
GROUP BY DbtrAgt
ORDER BY DbtrAgt;
"""

returned_data = pd.read_sql_query(returned_query, cnx)

# Close DB connection
cnx.close()

# Merge all data
final_merged_data = pd.merge(merged_cd_data, returned_data, on='Agt', how='outer')
final_merged_data[['transactions_R', 'amount_R']] = final_merged_data[['transactions_R', 'amount_R']].fillna(0)

# Fill any remaining NaNs
final_merged_data = final_merged_data.fillna(0)

# Reorder columns (optional, for presentation)
final_merged_data = final_merged_data[[
    'Agt', 'transactions_C', 'amount_C', 'transactions_D', 'amount_D', 'transactions_R', 'amount_R'
]]

# Create total row
total_row = pd.DataFrame([{
    'Agt': 'TOTAL',
    'transactions_C': final_merged_data['transactions_C'].sum(),
    'amount_C': final_merged_data['amount_C'].sum(),
    'transactions_D': final_merged_data['transactions_D'].sum(),
    'amount_D': final_merged_data['amount_D'].sum(),
    'transactions_R': final_merged_data['transactions_R'].sum(),
    'amount_R': final_merged_data['amount_R'].sum()
}])

# ---------- Display Final Table Without Index ----------
st.write(f"### Transactions Summary for Bank Prefix: {bank_prefix}")
st.dataframe(final_merged_data, use_container_width=True, hide_index=True)

# ---------- Display Totals Below the Table ----------
st.write("### Totals")
st.dataframe(total_row, use_container_width=True, hide_index=True)
