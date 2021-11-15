select distinct laws_json.id as id, name, number, comments, introductionDate as introduction_date,
url, transcriptUrl as transcript_url, stage_id, solution,
last_event_date, JSONExtractString(document,'name') as docname,
{{ref('doctypes')}}.id as doctype_id,
type_id as lawtype_id from gosduma.laws_json inner join {{ref('doctypes')}} on JSONExtractString(document,'type')={{ref('doctypes')}}.name 