

--complecated code
SELECT
    c.CdtrAgt,
    c.transactions AS credited_transactions,
    c.total_amount AS credited_amount,
    d.transactions AS debited_transactions,
    d.total_amount AS debited_amount,
    (c.total_amount - d.total_amount) AS total_balance
FROM
    (SELECT CdtrAgt, COUNT(*) AS transactions, SUM(IntrBkSttlmAmt) AS total_amount
     FROM Transaction_Pacs8_Inwards
     WHERE CdtrAgt LIKE 'ABNK%'
     GROUP BY CdtrAgt) c
LEFT JOIN
    (SELECT DbtrAgt, COUNT(*) AS transactions, SUM(IntrBkSttlmAmt) AS total_amount
     FROM Transaction_Pacs8_Outwards
     WHERE DbtrAgt LIKE 'ABNK%'
     GROUP BY DbtrAgt) d
ON c.CdtrAgt = d.DbtrAgt
ORDER BY c.CdtrAgt;



--If there are no debited transactions for a particular CdtrAgt, the debited_amount will be NULL. You may want to handle NULL values, for instance, by using COALESCE to treat NULL as 0:

COALESCE(d.total_amount, 0) AS debited_amount



