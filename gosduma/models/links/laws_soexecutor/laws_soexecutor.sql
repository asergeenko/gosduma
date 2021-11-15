select id as law_id, JSONExtractUInt(committees_soexecutor,'id') as committee_id
from gosduma.laws_json array join committees_soexecutor