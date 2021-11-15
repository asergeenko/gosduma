select law_id, toUInt64(JSONExtractString(deputies,'id')) as deputy_id
from (select id as law_id, JSONExtractArrayRaw(subject,'deputies') as deputies from gosduma.laws_json) array join deputies