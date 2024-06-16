SELECT
  celllabel,
  COUNT(*) AS count
FROM
  `physionet-data.eicu_crd.intakeoutput`
GROUP BY
  celllabel
ORDER BY
  count DESC