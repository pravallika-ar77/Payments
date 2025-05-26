import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Agent-to-Agent Transaction Filter", layout="wide")
st.title("Agent-to-Agent Transaction Filter")

# Connect to SQLite DB
engine = create_engine("sqlite:///payments.db")

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

# UI selection
agent_list = get_all_agents()
col1, col2 = st.columns(2)
with col1:
    selected_creditor = st.selectbox("Select Creditor Agent", [""] + agent_list)
with col2:
    selected_debitor = st.selectbox("Select Debitor Agent", [""] + agent_list)

# Query and show results
if selected_creditor and selected_debitor:
    st.markdown(f"## Transactions Between Creditor `{selected_creditor}` and Debitor `{selected_debitor}`")
    cnx = engine.connect()

    df_credit = pd.read_sql_query(f"""
        SELECT * FROM Transaction_Pacs8_Inwards
        WHERE CdtrAgt = '{selected_creditor}' AND DbtrAgt = '{selected_debitor}'
    """, cnx)

    df_debit = pd.read_sql_query(f"""
        SELECT * FROM Transaction_Pacs8_Outwards
        WHERE DbtrAgt = '{selected_debitor}' AND CdtrAgt = '{selected_creditor}'
    """, cnx)

    df_return = pd.read_sql_query(f"""
        SELECT * FROM Transaction_Pacs4
        WHERE DbtrAgt = '{selected_debitor}' AND CdtrAgt = '{selected_creditor}'
    """, cnx)

    cnx.close()

    credit_count = len(df_credit)
    debit_count = len(df_debit)
    return_count = len(df_return)

    credit_amount = df_credit["IntrBkSttlmAmt"].sum() if "IntrBkSttlmAmt" in df_credit.columns else 0
    debit_amount = df_debit["IntrBkSttlmAmt"].sum() if "IntrBkSttlmAmt" in df_debit.columns else 0
    return_amount = df_return["RtrdIntrBkSttlmAmt"].sum() if "RtrdIntrBkSttlmAmt" in df_return.columns else 0

    total_count = credit_count + debit_count + return_count

    if total_count > 0:
        # Display transaction tables
        if not df_credit.empty:
            st.subheader("Credit Transactions")
            st.dataframe(df_credit, use_container_width=True)

        if not df_debit.empty:
            st.subheader("Debit Transactions")
            st.dataframe(df_debit, use_container_width=True)

        if not df_return.empty:
            st.subheader("Return Transactions")
            st.dataframe(df_return, use_container_width=True)

        # Display summary after the tables
        st.markdown("### Transcations Information")
        st.markdown(f"""
 **{credit_count}** transactions from Credit Transactions  
   Amount = **{credit_amount:,.2f}**

 **{return_count}** transactions from Return Transactions  
   Amount = **{return_amount:,.2f}**

 **{debit_count}** transactions from Debit Transactions  
   Amount = **{debit_amount:,.2f}**

 **Total Transactions:** **{total_count}**
        """)

    else:
        st.info("No transactions found between the selected agents.")
