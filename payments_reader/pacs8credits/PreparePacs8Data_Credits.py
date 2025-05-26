import sqlite3

import pandas as pd

from random import choice

from generator.GenerateTransaction import uniqueid



unique_sequence = uniqueid()
all_records=[]
DbtrAgt_Ifsc=[]
amounts= [6001.65, 45678.22,7745.11,10086.22,3345.11]
DdtrAgt_Ifsc=['EBNK0000002','FBNK0000002','GBNK0000002','HBNK0000002']
csv_file= "Messages_Credits.csv"
message_table_name="Message_Pacs8_Inward"
Transaction_Pacs8_Inwards="Transaction_Pacs8_Inwards"
branch_choice=['2','3','4','5','6','7','8','9']

#sql='''
#     insert into Transaction_Pacs8_outwards(TxId,BizMsgIdr,EndToEndId,IntrBkSttlmAmt,IntrBkSttlmDt,DbtrAgt,CdtrAgt)
#     values (?,?,?,?,?,?,?) '''

sql=f"insert into {Transaction_Pacs8_Inwards}(TxId,BizMsgIdr,EndToEndId,IntrBkSttlmAmt,IntrBkSttlmDt,DbtrAgt,CdtrAgt) values (?,?,?,?,?,?,?)"


def generateTranId():
    return str(next(unique_sequence))


def readcsv_and_insert_into_db(filename,table,con):
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    df.to_sql(table, con, if_exists='replace')


def fetchmessages(con):
    curr = con.cursor()
    curr.execute(f"select BizMsgIdr,Rcvr,CreDt from {message_table_name}")
    return curr.fetchall()

def generatedbtragent(messages):
    for message in messages:
        BizMsgIdr = message[0]
        IntrBkSttlmDt = message[2]
        for i in range(10):
            TxId = generateTranId()
            EndToEndId = "/XUTR/" + TxId
            IntrBkSttlmAmt = choice(amounts)
            DbtrAgt=choice(DdtrAgt_Ifsc)
            CdtrAgt = message[1].replace('1', choice(branch_choice))
            record = tuple((TxId, BizMsgIdr, EndToEndId, IntrBkSttlmAmt,IntrBkSttlmDt, DbtrAgt, CdtrAgt))
            all_records.append(record)

def insert_into_db(con,transaction):
    curr = con.cursor()
    curr.execute(sql,transaction)

def deletetransactionentries(con):
    curr = con.cursor()
    curr.execute(f"delete from {Transaction_Pacs8_Inwards}")

try:
    with sqlite3.connect("../payments.db") as connection:
        readcsv_and_insert_into_db(csv_file,message_table_name,connection)
        generatedbtragent(fetchmessages(connection))
        deletetransactionentries(connection)
        for record in all_records:
            insert_into_db(connection,record)

        #a=1/0

        #connection.commit()
        print(f"Total transactions inserted are {len(all_records)}")

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
except Exception as error:
    print("Oops!", error)








