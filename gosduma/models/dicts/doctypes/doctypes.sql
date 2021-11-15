with JSONExtractString(document,'type') as name
select row_number() over(order by name) as id,name from gosduma.laws_json group by name