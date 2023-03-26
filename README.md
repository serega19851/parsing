# Парсинг онлйн библиотеки

Программа скачивает книги с сайта https://tululu.org/ 

## Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, если есть конфликт с Python2) для установки зависимостей.

```bash
pip install -r requirements.txt
```

## Запуск

Запускается на Linux(Python 3) или Windows:
```bash
>python manage.py --start_id (номер первой книги для скачивания) --end_id (номер последней книги для скачивания)
```


```bash
>python parse_tululu_category.py --start_page (начальный номер страницы) --end_page (последний номер страницы) 
```
Запуская скрипт parse_tululu_category.py можно прописывать необязательные аргументы :
- --dest_folder — путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
- --skip_imgs — не скачивать картинки
- --skip_txt — не скачивать книги
- --json_path — указать свой путь к *.json файлу с результатами

Пример:
```bash
>python parse_tululu_category.py --start_page 600 --end_page 700 --dest_folder --skip_txt
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).