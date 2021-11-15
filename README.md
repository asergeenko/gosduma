# Сервис для работы с открытыми данными Госдумы РФ
Исходные данные из [API Госдумы РФ](http://api.duma.gov.ru/) извлекаются с помощью [Apache Nifi](https://nifi.apache.org/) и приземляются в хранилище [Clickhouse](https://clickhouse.com/).

Репозиторий состоит из двух частей

1. [Data transformation](https://github.com/asergeenko/gosduma/tree/main/gosduma) - преобразование данных, приземлённых из API в 3НФ с помощью [dbt](https://www.getdbt.com/)
2. [Telegram бот](https://github.com/asergeenko/gosduma/tree/main/dumabot)

## Архитектура системы
<img src="https://github.com/asergeenko/gosduma/raw/main/schema.jpg"/>
