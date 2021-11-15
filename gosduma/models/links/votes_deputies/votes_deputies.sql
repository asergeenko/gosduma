select vote_id,deputy_id,{{ref('vote_results')}}.id as result_id from (
select distinct gosduma.votes_json.id as vote_id, gosduma.votes_json.dep_id as deputy_id, gosduma.votes_json.dep_result as result
from gosduma.votes_json array join gosduma.votes_json.dep_id,gosduma.votes_json.dep_result where result<>''
) as votes
join {{ref('vote_results')}} on name = votes.result