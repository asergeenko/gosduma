select law_id, JSONExtractUInt(departments,'id') as department_id 
from (select id as law_id, JSONExtractArrayRaw(subject,'departments') as departments from gosduma.laws_json) array join departments