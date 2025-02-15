### Бот для продаж услуг, обратной связи, помощи в работе.

Основные команды:\
/start - запуск бота для обычного пользователя

В проекте используются платежные системы:

- yookassa (https://yookassa.ru/)
- cryptomus (https://cryptomus.com)

Обновление от 30.09.2024

- Добавлена оплата криптой

Структура проекта:

```bazaar

project/
│
├── db/
│   ├── __init__.py        
│   ├── database.py      
│   └── settings_db.py      
├── system/<br>
│   ├── dispatcher.py      
│   └── ...<br>
├── setting/
│   └── user_data.db        
├── handlers/<br>
│   └── payment.py       
└── main.py   

```

Для обратной связи:\
TG - https://t.me/rusdnpy \
VK - https://vk.com/zh.vitaliy