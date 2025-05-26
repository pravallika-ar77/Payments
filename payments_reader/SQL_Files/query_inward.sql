--This query is for inwards to those bank  branches
SELECT CdtrAgt, COUNT(*) As transactions, SUM(IntrBkSttlmAmt) AS total_amount
FROM Transaction_Pacs8_Inwards
GROUP BY CdtrAgt
order by CdtrAgt;



--for particular bank branch inwards this is query
SELECT CdtrAgt, COUNT(*) As transactions, SUM(IntrBkSttlmAmt) AS total_amount
FROM Transaction_Pacs8_Inwards
where CdtrAgt like 'ABNK%'
GROUP BY CdtrAgt
order by CdtrAgt;