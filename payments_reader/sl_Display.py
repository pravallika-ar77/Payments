import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import configparser

# Page config
st.set_page_config(page_title="Agent Transactions Summary", layout="wide")
st.title("Agent Transactions Summary")

# Load .properties file
def load_properties():
    config = configparser.ConfigParser()
    with open("msg.properties") as f:
        config.read_string("[default]\n" + f.read())  # Fake section header
    return dict(config["default"])

props = load_properties()

# Helper to get property value with default fallback
def get_prop(key, default=None):
    return props.get(key, default)

# Function to get unique bank prefixes from the database
def get_bank_prefixes():
    cnx = create_engine('sqlite:///payments.db').connect()
    query = f"""
        SELECT DISTINCT SUBSTR({get_prop("tx_pacs8in_Credit", "CdtrAgt")}, 1, 4) AS prefix FROM Transaction_Pacs8_Inwards
        UNION
        SELECT DISTINCT SUBSTR({get_prop("tx_pacs8out_Debit", "DbtrAgt")}, 1, 4) AS prefix FROM Transaction_Pacs8_Outwards
        UNION
        SELECT DISTINCT SUBSTR({get_prop("tx_pacs4_Debit", "DbtrAgt")}, 1, 4) AS prefix FROM Transaction_Pacs4
    """
    df = pd.read_sql_query(text(query), cnx)
    cnx.close()
    prefixes = sorted(df['prefix'].dropna().unique().tolist())
    return [""] + prefixes  # Include empty string for "Select..."

# Get query parameters
query_params = st.query_params
selected_bank = query_params.get("bank", "")
selected_agent = query_params.get("selected_agent", "")

# Load bank prefixes dynamically
bank_prefixes = get_bank_prefixes()



# Layout alignment using columns
col1, col2 = st.columns([1, 5])

with col1:
    bank_prefix = st.selectbox(
        label="Bank Prefix",
        options=bank_prefixes,
        index=bank_prefixes.index(selected_bank) if selected_bank in bank_prefixes else 0,
        format_func=lambda x: "Select..." if x == "" else x,
        label_visibility="collapsed"
    )


# When bank is changed, update URL and clear selected_agent
if bank_prefix != selected_bank:
    st.query_params["bank"] = bank_prefix
    st.query_params.pop("selected_agent", None)  # Clear agent selection
    st.rerun()

# Stop if bank not selected
if bank_prefix == "":
    st.stop()

# Fetch and process transactions
def fetch_transaction_data(bank_prefix):
    cnx = create_engine('sqlite:///payments.db').connect()

    credited_query = f"""
    SELECT {get_prop("tx_pacs8in_Credit", "CdtrAgt")} AS Agt, 
           COUNT(*) AS Credit_Transaction_Count, 
           SUM({get_prop("tx_pacs8in_Amount", "IntrBkSttlmAmt")}) AS Credit_Transactions_Amount
    FROM Transaction_Pacs8_Inwards
    WHERE {get_prop("tx_pacs8in_Credit", "CdtrAgt")} LIKE '{bank_prefix}%'
    GROUP BY Agt
    """

    debited_query = f"""
    SELECT {get_prop("tx_pacs8out_Debit", "DbtrAgt")} AS Agt, 
           COUNT(*) AS Debit_Transaction_Count, 
           SUM({get_prop("tx_pacs8out_Amount", "IntrBkSttlmAmt")}) AS Debit_Transactions_Amount
    FROM Transaction_Pacs8_Outwards
    WHERE {get_prop("tx_pacs8out_Debit", "DbtrAgt")} LIKE '{bank_prefix}%'
    GROUP BY Agt
    """

    returned_query = f"""
    SELECT {get_prop("tx_pacs4_Debit", "DbtrAgt")} AS Agt, 
           COUNT(*) AS Return_Transaction_Count, 
           SUM({get_prop("tx_pacs4_Amount", "RtrdIntrBkSttlmAmt")}) AS Return_Transaction_Amount
    FROM Transaction_Pacs4
    WHERE {get_prop("tx_pacs4_Debit", "DbtrAgt")} LIKE '{bank_prefix}%'
    GROUP BY Agt
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

    int_cols = ["Credit_Transaction_Count", "Debit_Transaction_Count", "Return_Transaction_Count"]
    for col in int_cols:
        final_data[col] = final_data[col].astype(int)

    final_data["Total_Balance"] = final_data["Credit_Transactions_Amount"] - (
        final_data["Debit_Transactions_Amount"] + final_data["Return_Transaction_Amount"]
    )

    final_data = final_data[
        final_data["Agt"].between(f"{bank_prefix}0000002", f"{bank_prefix}0000009")
    ]

    return final_data

# Get summarized data
final_data = fetch_transaction_data(bank_prefix)

# Create agent links (with both bank & agent in URL)
def create_link(agent_code):
    return f'<a href="?bank={bank_prefix}&selected_agent={agent_code}" target="_self">{agent_code}</a>'

final_data["Agt"] = final_data["Agt"].apply(create_link)

# Add spacing and total row
empty_row = pd.DataFrame([{
    "Agt": "",
    "Credit_Transaction_Count": "",
    "Credit_Transactions_Amount": "",
    "Debit_Transaction_Count": "",
    "Debit_Transactions_Amount": "",
    "Return_Transaction_Count": "",
    "Return_Transaction_Amount": "",
    "Total_Balance": ""
}])

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

final_display_data = pd.concat([final_data, empty_row, total_row], ignore_index=True)

# Format float values
formatted_display_data = final_display_data.copy()
float_cols = ["Credit_Transactions_Amount", "Debit_Transactions_Amount", "Return_Transaction_Amount", "Total_Balance"]

for col in float_cols:
    formatted_display_data[col] = formatted_display_data[col].apply(
        lambda x: f"{int(x):,}" if isinstance(x, (int, float)) and str(x).strip() != "" else x
    )

# Display main summary table
st.markdown("### Agent Summary Table")
st.markdown(
    formatted_display_data.to_html(escape=False, index=False), unsafe_allow_html=True
)

# Detailed transaction view for selected agent
if selected_agent:
    st.markdown(f"## Detailed Transactions for {selected_agent}")
    cnx = create_engine('sqlite:///payments.db').connect()

    # Credit Transactions
    credit_query = f"SELECT * FROM Transaction_Pacs8_Inwards WHERE {get_prop('tx_pacs8in_Credit', 'CdtrAgt')} = '{selected_agent}'"
    credit_df = pd.read_sql_query(credit_query, cnx)
    if get_prop('tx_pacs8in_Credit', 'CdtrAgt') in credit_df.columns:
        credit_df = credit_df.drop(columns=[get_prop('tx_pacs8in_Credit', 'CdtrAgt')])
    st.subheader("Credit Transactions")
    st.dataframe(credit_df, use_container_width=True)

    # Debit Transactions
    debit_query = f"SELECT * FROM Transaction_Pacs8_Outwards WHERE {get_prop('tx_pacs8out_Debit', 'DbtrAgt')} = '{selected_agent}'"
    debit_df = pd.read_sql_query(debit_query, cnx)
    if get_prop('tx_pacs8out_Debit', 'DbtrAgt') in debit_df.columns:
        debit_df = debit_df.drop(columns=[get_prop('tx_pacs8out_Debit', 'DbtrAgt')])
    st.subheader("Debit Transactions")
    st.dataframe(debit_df, use_container_width=True)

    # Return Transactions
    return_query = f"SELECT * FROM Transaction_Pacs4 WHERE {get_prop('tx_pacs4_Debit', 'DbtrAgt')} = '{selected_agent}'"
    return_df = pd.read_sql_query(return_query, cnx)
    if get_prop('tx_pacs4_Debit', 'DbtrAgt') in return_df.columns:
        return_df = return_df.drop(columns=[get_prop('tx_pacs4_Debit', 'DbtrAgt')])
    st.subheader("Return Transactions")
    st.dataframe(return_df, use_container_width=True)

    cnx.close()