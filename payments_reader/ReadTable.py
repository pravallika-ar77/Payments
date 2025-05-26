# import the modules
import pandas as pd
from sqlalchemy import create_engine

# SQLAlchemy connectable
cnx = create_engine('sqlite:///payments.db').connect()

# table named 'contacts' will be returned as a dataframe.
debits = pd.read_sql_table('Transaction_Pacs8_Outwards', cnx,columns=["DbtrAgt","IntrBkSttlmAmt"])
#print(debits.tail(10))

#print(debits.groupby('DbtrAgt').agg(Total_Debit_Amount=("IntrBkSttlmAmt","sum"),No_of_Debits=("IntrBkSttlmAmt","count"),))

debits_df=debits.groupby('DbtrAgt').agg(Total_Debit_Amount=("IntrBkSttlmAmt","sum"),No_of_Debits=("IntrBkSttlmAmt","count"),)

#Total_Debits=debits.groupby('DbtrAgt').count()['IntrBkSttlmAmt'].sum()

credits = pd.read_sql_table('Transaction_Pacs8_Inwards', cnx,columns=["CdtrAgt","IntrBkSttlmAmt"])

#print(credits.groupby('CdtrAgt').agg(Total_Credit_Amount=("IntrBkSttlmAmt","sum"),No_of_Credits=("IntrBkSttlmAmt","count"),))

credits_df=credits.groupby('CdtrAgt').agg(Total_Credit_Amount=("IntrBkSttlmAmt","sum"),
                                    No_of_Credits=("IntrBkSttlmAmt","count"),)

print(pd.merge(debits_df,credits_df, how="outer",left_on="DbtrAgt",right_on="CdtrAgt",indicator=True))

#merged_data=pd.merge(debits_df,credits_df, how="outer",left_on="DbtrAgt",right_on="CdtrAgt")

#print(debits_df.join(credits_df,how='outer').head(100))