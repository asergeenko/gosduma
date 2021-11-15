with JSONExtractArrayRaw(subject,'departments') as deps,
dep_all as (
select arrayMap(s -> JSONExtractUInt(s, 'id'), deps) as id,
arrayMap(s -> JSONExtractString(s, 'name'), deps) as name,
arrayMap(s -> JSONExtractBool(s, 'isCurrent'), deps) as is_current,
arrayMap(s -> toDateOrNull(JSONExtractString(s, 'startDate')), deps) as start_date,
arrayMap(s -> toDateOrNull(JSONExtractString(s, 'stopDate')), deps) as stop_date from gosduma.laws_json
)
select distinct * from dep_all array join id,name,is_current,start_date,stop_date 