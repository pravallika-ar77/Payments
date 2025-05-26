import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Page configuration
st.set_page_config(page_title="Agent Transactions Summary", layout="wide")
st.title("Agent Transactions Summary")

# Bank prefixes
bank_prefixes = ["ABNK", "BBNK", "CBNK", "DBNK"]
bank_prefix = st.selectbox("Select a Bank Prefix", bank_prefixes)

# Fetch and process transactions
def fetch_transaction_data(bank_prefix):
    cnx = create_engine('sqlite:///payments.db').connect()

    credited_query = f"""
    SELECT CdtrAgt AS Agt, COUNT(*) AS Credit_Transaction_Count, 
           SUM(IntrBkSttlmAmt) AS Credit_Transactions_Amount
    FROM Transaction_Pacs8_Inwards
    WHERE CdtrAgt LIKE '{bank_prefix}%'
    GROUP BY CdtrAgt
    """

    debited_query = f"""
    SELECT DbtrAgt AS Agt, COUNT(*) AS Debit_Transaction_Count, 
           SUM(IntrBkSttlmAmt) AS Debit_Transactions_Amount
    FROM Transaction_Pacs8_Outwards
    WHERE DbtrAgt LIKE '{bank_prefix}%'
    GROUP BY DbtrAgt
    """

    returned_query = f"""
    SELECT DbtrAgt AS Agt, COUNT(*) AS Return_Transaction_Count, 
           SUM(RtrdIntrBkSttlmAmt) AS Return_Transaction_Amount
    FROM Transaction_Pacs4
    WHERE DbtrAgt LIKE '{bank_prefix}%'
    GROUP BY DbtrAgt
    """

    credited_data = pd.read_sql_query(credited_query, cnx)
    debited_data = pd.read_sql_query(debited_query, cnx)
    returned_data = pd.read_sql_query(returned_query, cnx)
    cnx.close()

    final_data = pd.merge(
        pd.merge(credited_data, debited_data, on="Agt", how="outer"),
        returned_data,
        on="Agt",
        how="outer"
    ).fillna(0)

    # Convert data types
    int_cols = ["Credit_Transaction_Count", "Debit_Transaction_Count", "Return_Transaction_Count"]
    #float_cols = ["Credit_Transactions_Amount", "Debit_Transactions_Amount", "Return_Transaction_Amount"]

    for col in int_cols:
        final_data[col] = final_data[col].astype(int)

    #for col in float_cols:
    #    final_data[col] = final_data[col].astype(float)

    # Calculate total balance
    final_data["Total_Balance"] = final_data["Credit_Transactions_Amount"] - (
        final_data["Debit_Transactions_Amount"] + final_data["Return_Transaction_Amount"]
    )

    # Filter required agents (e.g., ABNK0000002 to ABNK0000009)
    final_data = final_data[
        final_data["Agt"].between(f"{bank_prefix}0000002", f"{bank_prefix}0000009")
    ]

    return final_data

# Get the summarized data
final_data = fetch_transaction_data(bank_prefix)

# Create links for agents
def create_link(agent_code):
    return f'<a href="?selected_agent={agent_code}" target="_self">{agent_code}</a>'

final_data["Agt"] = final_data["Agt"].apply(create_link)

# Add empty row for spacing
empty_row = pd.DataFrame([{
    "Agt": " ",
    "Credit_Transaction_Count": " ",
    "Credit_Transactions_Amount": " ",
    "Debit_Transaction_Count": " ",
    "Debit_Transactions_Amount": " ",
    "Return_Transaction_Count": " ",
    "Return_Transaction_Amount": " ",
    "Total_Balance": " "
}])

# Total row
total_row = pd.DataFrame([{
    "Agt": "TOTAL",
    "Credit_Transaction_Count": int(final_data["Credit_Transaction_Count"].sum()),
    "Credit_Transactions_Amount": final_data["Credit_Transactions_Amount"].sum(),
    "Debit_Transaction_Count": int(final_data["Debit_Transaction_Count"].sum()),
    "Debit_Transactions_Amount": final_data["Debit_Transactions_Amount"].sum(),
    "Return_Transaction_Count": int(final_data["Return_Transaction_Count"].sum()),
    "Return_Transaction_Amount": final_data["Return_Transaction_Amount"].sum(),
    "Total_Balance": final_data["Total_Balance"].sum()
}])

# Combine all data
final_display_data = pd.concat([final_data, empty_row, total_row], ignore_index=True)

# Format float values to display as whole numbers (with commas)
formatted_display_data = final_display_data.copy()
float_cols = ["Credit_Transactions_Amount", "Debit_Transactions_Amount", "Return_Transaction_Amount", "Total_Balance"]

for col in float_cols:
    formatted_display_data[col] = formatted_display_data[col].apply(
        lambda x: f"{int(x):,}" if isinstance(x, (int, float)) and str(x).strip() != "" else x
    )

# Display the summary table
st.markdown("### Agent Summary Table")
st.markdown(
    formatted_display_data.to_html(escape=False, index=False), unsafe_allow_html=True
)

# ------ Detailed Transaction View for a Selected Agent ------
selected_agent = st.query_params.get("selected_agent")

if selected_agent:
    st.markdown(f"## Detailed Transactions for `{selected_agent}`")
    cnx = create_engine('sqlite:///payments.db').connect()

    # Credit Transactions
    credit_query = f"SELECT * FROM Transaction_Pacs8_Inwards WHERE CdtrAgt = '{selected_agent}'"
    credit_df = pd.read_sql_query(credit_query, cnx)
    if "CdtrAgt" in credit_df.columns:
        credit_df = credit_df.drop(columns=["CdtrAgt"])
    st.subheader("Credit Transactions")
    st.dataframe(credit_df, use_container_width=True)

    # Debit Transactions
    debit_query = f"SELECT * FROM Transaction_Pacs8_Outwards WHERE DbtrAgt = '{selected_agent}'"
    debit_df = pd.read_sql_query(debit_query, cnx)
    if "DbtrAgt" in debit_df.columns:
        debit_df = debit_df.drop(columns=["DbtrAgt"])
    st.subheader("Debit Transactions")
    st.dataframe(debit_df, use_container_width=True)

    # Return Transactions
    return_query = f"SELECT * FROM Transaction_Pacs4 WHERE DbtrAgt = '{selected_agent}'"
    return_df = pd.read_sql_query(return_query, cnx)
    if "DbtrAgt" in return_df.columns:
        return_df = return_df.drop(columns=["DbtrAgt"])
    st.subheader("Return Transactions")
    st.dataframe(return_df, use_container_width=True)

    cnx.close()
