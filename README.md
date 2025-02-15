# Тестовое задание на стажировку Авито

## Выполнено:

1. Написан API для покупки товаров на Flask;
2. Настроена аутентификация по JWT токенам;
3. Реализованы юнит-тесты на unittest - покрытие более 90% строк кода;
4. Реализовано два E2E теста на unittest на сценарии покупки товаров и перевода монет;
5. Подключена база Postgres для сохранения данных пользователей, товаров и транзакций;
6. Сконфигурирован docker-compose;
7. Настроен линтер pylint.

## Запуск в докере:

* Для запуска проекта в докере потребуется файл с именем `docker.env`. Найти пример можно в `example_docker.env`.
* Собрать и запустить проект: `docker-compose up --build`.
* Запустить тесты: `docker exec avito-shop-service bash -c "cd .. && python3 -m unittest discover -s app -t ."`
* Запустить линтер: `docker exec avito-shop-service bash -c "python3 -m pylint --rcfile=pylintrc api"`

*Получение JWT_SECRET_KEY для файла `docker.env`:* 

```python
import secrets
jwt_secret_key = secrets.token_hex(32)
print(jwt_secret_key)
```

## Конфигурация файла линтера pylintrc:

- `pylintrc` был сгенерирован автоматически командой `pylint --generate-rcfile > /.pylintrc`. В файле была изменена
  секция MESSAGES-CONTROL, чтобы выводились только нужные предупреждения.

