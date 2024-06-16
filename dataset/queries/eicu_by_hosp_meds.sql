SELECT
  pat.hospitalid,
  drugname,
  routeadmin,
  COUNT(*) AS count
FROM
  `physionet-data.eicu_crd.medication` med
LEFT JOIN
  `physionet-data.eicu_crd.patient` pat
ON
  pat.patientunitstayid = med.patientunitstayid
WHERE
  drugname IS NOT NULL
  AND routeadmin IS NOT NULL
GROUP BY
  hospitalid,
  drugname,
  routeadmin
ORDER BY
  count DESC