# Service for Working with Open Data from the Russian State Duma

Source data from the [Russian State Duma API](http://api.duma.gov.ru/) is extracted using [Apache NiFi](https://nifi.apache.org/) and stored in [ClickHouse](https://clickhouse.com/).

The repository consists of two parts:

1. [Data Transformation](https://github.com/asergeenko/gosduma/tree/main/gosduma) - transforming data from the API into 3NF using [dbt](https://www.getdbt.com/)
2. [Telegram Bot](https://github.com/asergeenko/gosduma/tree/main/dumabot)

## System Architecture
<img src="https://github.com/asergeenko/gosduma/raw/main/schema.jpg"/>
