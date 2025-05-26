
--This is query for outward debits bank wise and their branch wise

SELECT DbtrAgt, COUNT(*) As transactions, SUM(IntrBkSttlmAmt) AS total_amount
FROM Transaction_Pacs8_Outwards
GROUP BY DbtrAgt
order by DbtrAgt;



--if we need to see the transactions of a particular bank then query must be like

SELECT DbtrAgt, COUNT(*) As transactions, SUM(IntrBkSttlmAmt) AS total_amount
FROM Transaction_Pacs8_Outwards
where DbtrAgt like 'ABNK%'
GROUP BY DbtrAgt
order by DbtrAgt;


--ABNK% can be replaced with BBNK%, CBNK% etc