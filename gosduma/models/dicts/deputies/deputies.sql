select dep.id,name,isCurrent as is_current,pos.id as position_id from gosduma.deputies_json dep inner join {{ref('positions')}} pos on dep.position=pos.name 