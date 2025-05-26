import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Streamlit page settings
st.set_page_config(page_title="Transaction Viewer", layout="wide")
st.title("Bank Transaction Details (0000002 to 0000009)")

# Connect to the SQLite database
engine = create_engine('sqlite:///payments.db')
cnx = engine.connect()

# Set Pandas options to show all
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# List of bank agent prefixes
bank_codes = ['ABNK', 'BBNK', 'CBNK', 'DBNK']

# Loop through bank codes (ABNK, BBNK, CBNK, DBNK) and agent numbers 0000002 to 0000009
for bank_code in bank_codes:
    for i in range(2, 10):
        agent_code = f"{bank_code}000000{i}"
        st.markdown(f"---\n## Branch: `{agent_code}`")

        # --- Credit Transactions ---

        credit_query = f"""
        SELECT *
        FROM Transaction_Pacs8_Inwards
        WHERE CdtrAgt = '{agent_code}'
        """
        credit_df = pd.read_sql_query(credit_query, cnx)
        with st.expander(f" View Credit Transactions for {agent_code}"):
            st.dataframe(credit_df, use_container_width=True)

        # --- Debit Transactions ---
        debit_query = f"""
        SELECT *
        FROM Transaction_Pacs8_Outwards
        WHERE DbtrAgt = '{agent_code}'
        """
        debit_df = pd.read_sql_query(debit_query, cnx)
        with st.expander(f"View Debit Transactions for {agent_code}"):
            st.dataframe(debit_df, use_container_width=True)



        # --- Return Transactions ---
        debit_query = f"""
        SELECT *
        FROM Transaction_Pacs4
        WHERE DbtrAgt = '{agent_code}'
        """
        debit_df = pd.read_sql_query(debit_query, cnx)
        with st.expander(f"View Return Transactions for {agent_code}"):
            st.dataframe(debit_df, use_container_width=True)

# Close DB connection
cnx.close()
