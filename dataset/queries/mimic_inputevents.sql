SELECT
  ie.itemid,
  di.label,
  COUNT(*) AS count,
  CASE
    WHEN ie.itemid IN (220949, 220950, 220952, 225158, 225159, 225823, 225825, 225827, 225828, 225941, 226089, 226361, 226364, 
    226365, 227533, 225161, 228140, 228141, 228142, 220865, 220951, 220953, 220975, 220977, 220979, 220980, 221000, 221001, 
    221002, 221003, 221014, 221017, 221211, 220954, 220955, 220956, 220958, 220959, 220960, 220961, 220962, 220963, 220964, 
    220965, 220966, 220967, 220968, 221212, 221213, 220861, 220863) THEN 1
    ELSE 0
    END
  AS iv_fluid
FROM
  `physionet-data.mimiciv_icu.inputevents` ie
LEFT JOIN
  `physionet-data.mimiciv_icu.d_items` di
ON
  ie.itemid = di.itemid
GROUP BY
  ie.itemid,
  di.label,
  iv_fluid

ORDER BY
  count DESC
  -- WHERE