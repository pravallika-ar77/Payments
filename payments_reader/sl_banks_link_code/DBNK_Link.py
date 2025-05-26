import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Streamlit app title
st.title("Agent Transactions Summary - DBNK")

# Set bank prefix
bank_prefix = "DBNK"

# Connect to database
cnx = create_engine('sqlite:///payments.db').connect()

# ---------- Fetch Credit, Debit, and Return Transactions ----------

credited_query = f"""
SELECT CdtrAgt AS Agt, COUNT(*) AS Credit_Transaction_Count, SUM(IntrBkSttlmAmt) AS Credit_Transactions_Amount
FROM Transaction_Pacs8_Inwards
WHERE CdtrAgt LIKE '{bank_prefix}%'
GROUP BY CdtrAgt
"""

debited_query = f"""
SELECT DbtrAgt AS Agt, COUNT(*) AS Debit_Transaction_Count, SUM(IntrBkSttlmAmt) AS Debit_Transactions_Amount
FROM Transaction_Pacs8_Outwards
WHERE DbtrAgt LIKE '{bank_prefix}%'
GROUP BY DbtrAgt
"""

returned_query = f"""
SELECT DbtrAgt AS Agt, COUNT(*) AS Return_Transaction_Count, SUM(RtrdIntrBkSttlmAmt) AS Return_Transaction_Amount
FROM Transaction_Pacs4
WHERE DbtrAgt LIKE '{bank_prefix}%'
GROUP BY DbtrAgt
"""

# Read data from database
credited_data = pd.read_sql_query(credited_query, cnx)
debited_data = pd.read_sql_query(debited_query, cnx)
returned_data = pd.read_sql_query(returned_query, cnx)

# Close database connection
cnx.close()

# Merge all transaction types
final_data = pd.merge(pd.merge(credited_data, debited_data, on='Agt', how='outer').fillna(0), returned_data, on='Agt', how='outer').fillna(0)

# Compute Total Balance
final_data["Total_Balance"] = final_data["Credit_Transactions_Amount"] - (
    final_data["Debit_Transactions_Amount"] + final_data["Return_Transaction_Amount"]
)

# Filter only required agents (DBNK0000002 to DBNK0000009)
final_data = final_data[final_data["Agt"].between(f"{bank_prefix}0000002", f"{bank_prefix}0000009")]

# Create clickable links for each agent
def create_link(agent_code):
    return f'<a href="?selected_agent={agent_code}" target="_self">{agent_code}</a>'

final_data["Agt"] = final_data["Agt"].apply(lambda x: create_link(x) if pd.notna(x) else '')

# Create an empty row
empty_row = pd.DataFrame([{}])  # Empty row placeholder

# Compute total row
total_row = pd.DataFrame([{
    "Agt": "TOTAL",
    "Credit_Transaction_Count": final_data["Credit_Transaction_Count"].sum(),
    "Credit_Transactions_Amount": final_data["Credit_Transactions_Amount"].sum(),
    "Debit_Transaction_Count": final_data["Debit_Transaction_Count"].sum(),
    "Debit_Transactions_Amount": final_data["Debit_Transactions_Amount"].sum(),
    "Return_Transaction_Count": final_data["Return_Transaction_Count"].sum(),
    "Return_Transaction_Amount": final_data["Return_Transaction_Amount"].sum(),
    "Total_Balance": final_data["Total_Balance"].sum()
}])

# Append empty row and total row
final_display_data = pd.concat([final_data, empty_row, total_row], ignore_index=True)

# Convert table to HTML with embedded links
styled_table = final_display_data.to_html(index=False, escape=False)

# Display Table with Clickable Agent Codes
st.markdown("### Click on a Branch (Agent Code) to View Transactions")
st.markdown(styled_table, unsafe_allow_html=True)

# ------ Fetch Selected Agent for Detailed Transactions ------
selected_agent = st.query_params.get("selected_agent")

if selected_agent:
    st.write(f"## Transactions for {selected_agent}")

    # Connect to database again for detailed transactions
    cnx = create_engine('sqlite:///payments.db').connect()

    # Fetch Credit Transactions
    credit_query = f"SELECT * FROM Transaction_Pacs8_Inwards WHERE CdtrAgt = '{selected_agent}'"
    credit_df = pd.read_sql_query(credit_query, cnx)
    st.write(f"### Credit Transactions for {selected_agent}")
    st.dataframe(credit_df, use_container_width=True)

    # Fetch Debit Transactions
    debit_query = f"SELECT * FROM Transaction_Pacs8_Outwards WHERE DbtrAgt = '{selected_agent}'"
    debit_df = pd.read_sql_query(debit_query, cnx)
    st.write(f"### Debit Transactions for {selected_agent}")
    st.dataframe(debit_df, use_container_width=True)

    # Fetch Return Transactions
    return_query = f"SELECT * FROM Transaction_Pacs4 WHERE DbtrAgt = '{selected_agent}'"
    return_df = pd.read_sql_query(return_query, cnx)
    st.write(f"### Return Transactions for {selected_agent}")
    st.dataframe(return_df, use_container_width=True)

    # Close DB connection
    cnx.close()
