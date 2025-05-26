
create table IF NOT EXISTS Message_Pacs8_Inward (
        BizMsgIdr TEXT PRIMARY KEY,
        Sndr TEXT NOT NULL,
        Rcvr TEXT NOT NULL,
        CreDt DATE NOT NULL
        );

create table IF NOT EXISTS Transaction_Pacs8_Inwards (

       TxId TEXT PRIMARY KEY,
       BizMsgIdr TEXT NOT NULL,
       EndToEndId TEXT NOT NULL,
       IntrBkSttlmAmt REAL NOT NULL,
       IntrBkSttlmDt DATE NOT NULL,
       DbtrAgt TEXT NOT NULL,
       CdtrAgt TEXT NOT NULL,
       FOREIGN KEY (BizMsgIdr)
       REFERENCES Message_Pacs8_Inward (BizMsgIdr)
        ON UPDATE CASCADE
        ON DELETE CASCADE
       );

 select * from Message_Pacs8_Inward where BizMsgIdr='1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g'

select * from Transaction_Pacs8_Inwards where BizMsgIdr='1Ke4JmBaZrgERrFiUGwBNxS9CR7osLBf1g'


