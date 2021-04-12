# News collector
---  
https://vk.com/auto_it_news  
https://t.me/auto_it_news
---
1. Для использования VK бота Вам необходимо:  
    - Создать группу с настройками бота
    - Создать файл settings.py содержащий:
      - TOKEN - токен Вашей группы
      - ID_GROUP - id Вашей группы
      - APP_ID - id Вашего приложения для постинга
      - ACCESS_TOKEN - токен Вашего приложения
      - IMAGE_EXTENSION - список расширений картинок ['jpg', 'jpeg', 'png']
      - MY_ID - id администратора группы
      - TIME_UPDATE_MINUTES - время обновления постов
2. Для использования Telegram бота Вам необходимо:
   - Создать бота
   - Создать файл settings.py содержащий:
      - TOKEN - токен Вашего бота
      - TIME_UPDATE_MINUTES - время обновления постов
      - IMAGE_EXTENSION - список расширений картинок ['jpg', 'jpeg', 'png']
3. Для использования Email рассылки Вам необходимо:
   - Создать почту
   - Создать файл settings.py содержащий:
      - TIME_UPDATE_MINUTES - время обновления постов
      - LOGIN - логин от почты
      - PASSWORD - пароль от почты
      - EMAIL - email адрес
      - IMAGE_EXTENSION - список расширений картинок ['jpg', 'jpeg', 'png']
    