SELECT s1.number AS Panel_Num,  s2.number AS Lower_LPALID, s2.id AS Lower_LPAL_Straw_Loc, s3.number AS Upper_LPALID, s3.id AS Upper_LPAL_Straw_Loc

FROM procedure_details_pan1 AS procD /*Works to get data since loading pallets was added to proc.1*/
--FROM procedure_details_pan2 AS procD /*Works to get the required data from when loading pallets was in proc.2*/

INNER JOIN procedure as p1 ON p1.id = procD.procedure

INNER JOIN straw_location as s1 ON s1.id = p1.straw_location
INNER JOIN straw_location as s2 ON s2.id = procD.lpal_bot
INNER JOIN straw_location as s3 ON s3.id = procD.lpal_top

ORDER BY Panel_Num