SELECT
    'ABNK0000002' AS Agt,

    -- Credits (Inward)
    (SELECT SUM(IntrBkSttlmAmt)
     FROM Transaction_Pacs8_Inwards
     WHERE CdtrAgt = 'ABNK0000002') AS credited_amount,

    -- Debits (Outward)
    (SELECT SUM(IntrBkSttlmAmt)
     FROM Transaction_Pacs8_Outwards
     WHERE DbtrAgt = 'ABNK0000002') AS debited_amount,

    -- Net Total = Credits - Debits
    (
        (SELECT SUM(IntrBkSttlmAmt)
         FROM Transaction_Pacs8_Inwards
         WHERE CdtrAgt = 'ABNK0000002')
        -
        (SELECT SUM(IntrBkSttlmAmt)
         FROM Transaction_Pacs8_Outwards
         WHERE DbtrAgt = 'ABNK0000002')
    ) AS total_balance;
