import sqlite3
import pandas as pd
from random import choice
from generator.GenerateTransaction import uniqueid

# Initialize unique sequence generator and lists
unique_sequence = uniqueid()
all_records = []
CdtrAgt_Ifsc = ['EBNK0000002', 'FBNK0000001', 'GBNK0000001', 'HBNK0000001']
amounts = [5001.65, 35678.22, 6745.11, 9086.22, 2345.11]
DbtrAgt_Ifsc = ['EBNK0000002', 'FBNK0000001', 'GBNK0000001', 'HBNK0000001']
csv_file = "Messages_Returns.csv"
message_table_name = "Message_Pacs4"
Transaction_Pacs4 = "Transaction_Pacs4"
branch_choice = ['2', '3', '4', '5', '6', '7', '8', '9']

sql = '''
     insert into Transaction_Pacs4(RtrId,BizMsgIdr,OrgnlTxId,OrgnlEndToEndId,RtrdIntrBkSttlmAmt,IntrBkSttlmDt,DbtrAgt,CdtrAgt)
     values (?,?,?,?,?,?,?,?)'''

sql = f"insert into {Transaction_Pacs4}(RtrId,BizMsgIdr,OrgnlTxId,OrgnlEndToEndId,RtrdIntrBkSttlmAmt,IntrBkSttlmDt,DbtrAgt,CdtrAgt) values (?,?,?,?,?,?,?,?)"

def generateTranId():
    return str(next(unique_sequence))

def readcsv_and_insert_into_db(filename, table, con):
    # Read CSV and insert into database table
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    df.to_sql(table, con, if_exists='replace')

def fetchmessages(con):
    # Fetch messages from database (No print statement here)
    curr = con.cursor()
    curr.execute(f"select BizMsgIdr, Sndr, CreDt from {message_table_name}")
    messages = curr.fetchall()
    return messages

def generatedbtragent(messages):
    if not messages:
        print("No messages found!")
        return

    for message in messages:
        BizMsgIdr = message[0]
        IntrBkSttlmDt = message[2]
        for i in range(10):
            # Generate transaction details
            RtrId = generateTranId()
            OrgnlTxId = "/XUTR/"
            OrgnlEndToEndId = "/XUTR/" + RtrId
            TtrdIntrBkSttlmAmt = choice(amounts)
            DbtrAgt = message[1].replace('1', choice(branch_choice))  # Randomly replace branch
            CdtrAgt = choice(CdtrAgt_Ifsc)  # Random creditor
            record = tuple((RtrId, BizMsgIdr, OrgnlTxId, OrgnlEndToEndId, TtrdIntrBkSttlmAmt, IntrBkSttlmDt, DbtrAgt, CdtrAgt))
            all_records.append(record)

def insert_into_db(con, transaction):
    # Insert the transaction record into the database
    curr = con.cursor()
    curr.execute(sql, transaction)

def deletetransactionentries(con):
    # Delete all previous entries from the transaction table
    curr = con.cursor()
    curr.execute(f"delete from {Transaction_Pacs4}")

try:
    with sqlite3.connect("../payments.db") as connection:
        # Read the CSV and insert into database
        readcsv_and_insert_into_db(csv_file, message_table_name, connection)

        # Generate transactions
        messages = fetchmessages(connection)
        generatedbtragent(messages)

        # Clean previous entries and insert new records
        deletetransactionentries(connection)
        for record in all_records:
            insert_into_db(connection, record)

        # Print total number of transactions inserted
        print(f"Total transactions inserted are {len(all_records)}")

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
except Exception as error:
    print("Oops!", error)