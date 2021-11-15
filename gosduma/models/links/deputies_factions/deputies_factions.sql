select id as deputy_id,fac_id as faction_id,
       fac_startDate as start_date,
       fac_endDate as end_date from gosduma.deputies_json array join fac_id,fac_startDate,fac_endDate