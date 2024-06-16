SELECT
  drugname,
  routeadmin,
  COUNT(*) AS count
FROM
  `physionet-data.eicu_crd.medication`
WHERE
  drugname IS NOT NULL
  AND routeadmin IS NOT NULL
GROUP BY
  drugname,
  routeadmin
ORDER BY
  count DESC