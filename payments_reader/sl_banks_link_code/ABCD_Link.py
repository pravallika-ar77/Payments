import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Agent Transactions Summary", layout="wide")
st.title("Agent Transactions Summary")

# Connect to database
engine = create_engine('sqlite:///payments.db')

# Dynamically fetch all bank prefixes
@st.cache_data
def get_bank_prefixes():
    query = """
        SELECT DISTINCT SUBSTR(CdtrAgt, 1, 4) AS prefix FROM Transaction_Pacs8_Inwards
        UNION
        SELECT DISTINCT SUBSTR(DbtrAgt, 1, 4) FROM Transaction_Pacs8_Outwards
        UNION
        SELECT DISTINCT SUBSTR(DbtrAgt, 1, 4) FROM Transaction_Pacs4
    """
    df = pd.read_sql_query(query, engine)
    return sorted(df['prefix'].dropna().unique().tolist())

bank_prefixes = get_bank_prefixes()
bank_prefix = st.selectbox("Select a Bank Prefix", [""] + bank_prefixes)

if not bank_prefix:
    st.stop()

# Fetch transaction summary for selected prefix
def fetch_transaction_data(prefix):
    cnx = engine.connect()

    credited = f"""
    SELECT CdtrAgt AS Agt, COUNT(*) AS Credit_Transaction_Count, SUM(IntrBkSttlmAmt) AS Credit_Transactions_Amount
    FROM Transaction_Pacs8_Inwards
    WHERE CdtrAgt LIKE '{prefix}%'
    GROUP BY CdtrAgt
    """
    debited = f"""
    SELECT DbtrAgt AS Agt, COUNT(*) AS Debit_Transaction_Count, SUM(IntrBkSttlmAmt) AS Debit_Transactions_Amount
    FROM Transaction_Pacs8_Outwards
    WHERE DbtrAgt LIKE '{prefix}%'
    GROUP BY DbtrAgt
    """
    returned = f"""
    SELECT DbtrAgt AS Agt, COUNT(*) AS Return_Transaction_Count, SUM(RtrdIntrBkSttlmAmt) AS Return_Transaction_Amount
    FROM Transaction_Pacs4
    WHERE DbtrAgt LIKE '{prefix}%'
    GROUP BY DbtrAgt
    """

    df_credit = pd.read_sql_query(credited, cnx)
    df_debit = pd.read_sql_query(debited, cnx)
    df_return = pd.read_sql_query(returned, cnx)

    cnx.close()

    df_final = pd.merge(pd.merge(df_credit, df_debit, on='Agt', how='outer'), df_return, on='Agt', how='outer')
    df_final = df_final.fillna("")

    df_final["Total_Balance"] = df_final.apply(lambda row: (
        float(row["Credit_Transactions_Amount"] or 0) -
        (float(row["Debit_Transactions_Amount"] or 0) + float(row["Return_Transaction_Amount"] or 0))
    ), axis=1)

    return df_final

summary_df = fetch_transaction_data(bank_prefix)

st.markdown("### Agent Summary Table")
st.dataframe(summary_df, use_container_width=True)

# Get ALL CdtrAgt and DbtrAgt from all 3 tables
@st.cache_data
def get_all_agents():
    q = """
        SELECT CdtrAgt AS agent FROM Transaction_Pacs8_Inwards
        UNION
        SELECT DbtrAgt FROM Transaction_Pacs8_Outwards
        UNION
        SELECT CdtrAgt FROM Transaction_Pacs4
        UNION
        SELECT DbtrAgt FROM Transaction_Pacs4
    """
    df = pd.read_sql_query(q, engine)
    return sorted(df['agent'].dropna().unique().tolist())

agent_list = get_all_agents()

# Dropdowns for selecting creditor and debitor
col1, col2 = st.columns(2)
with col1:
    selected_creditor = st.selectbox("Select Creditor Agent", [""] + agent_list)
with col2:
    selected_debitor = st.selectbox("Select Debitor Agent", [""] + agent_list)

# Show matching transactions from all 3 tables
if selected_creditor and selected_debitor:
    st.markdown(f"## Transactions Between Creditor `{selected_creditor}` and Debitor `{selected_debitor}`")
    cnx = engine.connect()

    credit_q = f"""
    SELECT * FROM Transaction_Pacs8_Inwards
    WHERE CdtrAgt = '{selected_creditor}' AND DbtrAgt = '{selected_debitor}'
    """
    debit_q = f"""
    SELECT * FROM Transaction_Pacs8_Outwards
    WHERE DbtrAgt = '{selected_debitor}' AND CdtrAgt = '{selected_creditor}'
    """
    return_q = f"""
    SELECT * FROM Transaction_Pacs4
    WHERE DbtrAgt = '{selected_debitor}' AND CdtrAgt = '{selected_creditor}'
    """

    df_credit = pd.read_sql_query(credit_q, cnx)
    df_debit = pd.read_sql_query(debit_q, cnx)
    df_return = pd.read_sql_query(return_q, cnx)
    cnx.close()

    if not df_credit.empty:
        st.subheader("Credit Transactions")
        st.dataframe(df_credit, use_container_width=True)
    if not df_debit.empty:
        st.subheader("Debit Transactions")
        st.dataframe(df_debit, use_container_width=True)
    if not df_return.empty:
        st.subheader("Return Transactions")
        st.dataframe(df_return, use_container_width=True)

    if df_credit.empty and df_debit.empty and df_return.empty:
        st.info("No transactions found between the selected agents.")
