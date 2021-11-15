select id as law_id, JSONExtractUInt(committees_profile,'id') as committee_id
from gosduma.laws_json array join committees_profile