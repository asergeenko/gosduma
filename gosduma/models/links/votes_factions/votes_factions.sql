select distinct gosduma.votes_json.id as vote_id, gosduma.votes_json.fac_id as faction_id, gosduma.votes_json.fac_total as total,
gosduma.votes_json.fac_for as for, gosduma.votes_json.fac_against as against,
gosduma.votes_json.fac_abstain as abstain, gosduma.votes_json.fac_absent as absent
from gosduma.votes_json array join gosduma.votes_json.fac_id,gosduma.votes_json.fac_total,gosduma.votes_json.fac_for,
gosduma.votes_json.fac_against,gosduma.votes_json.fac_abstain,gosduma.votes_json.fac_absent