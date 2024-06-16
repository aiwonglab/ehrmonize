SELECT
  DISTINCT labtypeid,
  CASE 
    WHEN labtypeid = 1 THEN 'chemistry'
    WHEN labtypeid = 2 THEN 'drug_level'
    WHEN labtypeid = 3 THEN 'hemo'
    WHEN labtypeid = 4 THEN 'misc'
    WHEN labtypeid = 5 THEN 'non-mapped'
    WHEN labtypeid = 6 THEN 'sensitive'
    WHEN labtypeid = 7 THEN 'abg'
    ELSE 'unknown'
  END AS labtype,
  labname
FROM
  `physionet-data.eicu_crd.lab`
ORDER BY
  labtypeid DESC
