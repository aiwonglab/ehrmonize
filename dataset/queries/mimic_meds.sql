SELECT
  drug,
  ndc,
  route,
  COUNT(*) AS count
FROM
  `physionet-data.mimiciv_hosp.prescriptions`
WHERE
      drug IS NOT NULL
  AND ndc IS NOT NULL
  AND ndc <> "0"
  AND route IS NOT NULL
GROUP BY
  drug,
  ndc,
  route
ORDER BY
  count DESC,
  drug ASC,
  route ASC