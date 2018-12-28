
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a47323eac22e4ae984c5306ad85ea354)](https://app.codacy.com/app/Nemiroff/script.elementum.nova?utm_source=github.com&utm_medium=referral&utm_content=Nemiroff/script.elementum.nova&utm_campaign=Badge_Grade_Dashboard)
# Elementum Nova [![Build Status](https://travis-ci.org/Nemiroff/script.elementum.nova.svg?branch=master)](https://travis-ci.org/Nemiroff/script.elementum.nova) [![GitHub release](https://img.shields.io/github/release/Nemiroff/script.elementum.nova.svg)](https://github.com/Nemiroff/script.elementum.nova/releases/latest) [![Telegram](https://img.shields.io/badge/telegram-%40Elementum__nova-blue.svg)](https://t.me/elementum_nova)
### Возможности
- Ну вроде быстрый
- Не требует установку дополнительных аддонов
- Не требуется запуск сервиса в фоне
- Простое включение и отключение профайдера в настройках. А так-же фильтрация их по типу контента
- Возможность простого переназначения настроек провайдера без вмешательства в код плагина


### Установка

Скачайте последнюю версию с https://nemiroff.surge.sh
Для Kodi 17 и выше включите в настройках Неизвестные источники
Установите как обычный zip аддон.
Для автообновления можно поставить репозиторий с https://nemiroff.github.com/kodi_repo/ или из search.db от bigbax

### Добавление / редактирование провайдеров

**В данный момент возможно добавление только открытых провайдера (без ввода логина и пароля) через .json

Вы можете изменить любой параметр провайдера в файле `providers.json`, но ваши изменения будут потеряны при следующем обновлении.
Для того, чтобы этого не произошло Вам требуется создать файл `overrides.py` в папке профиля,
например: `~/.kodi/userdata/addon_data/script.elementum.nova/overrides.py`. 
Поместите Ваши изменения в переменную `overrides` что бы выглядело так:
```
overrides = {
    'lostfilm': {
        'name': 'LostFilm.TV'
    }
}
```
Добавление пользовательского провайдера не сложно, хоть вы будете использовать файл JSON.
Можно использовать файл для каждого провайдера отдельно или один со всеми вашими провайдерами.
Просто создайте файл с расширением `.json` в папке `providers` которая находится в Вашем профиле, например:
`~/.kodi/userdata/addon_data/script.elementum.nova/providers/lostfilm.json`
содержащим (желательно с `"subpage": false`):
```
{
    "lostfilm": {
        "anime_extra": "",
        "anime_keywords": "{title:original} {episode}",
        "anime_query": "EXTRA",
        "base_url": "http://www.lostfilm.tv/search/QUERY/1/",
        "color": "FFF14E13",
        "general_extra": "",
        "general_keywords": "{title}",
        "general_query": "EXTRA",
        "language": null,
        "charset": "windows-1251",
        "login_failed": "",
        "login_object": "",
        "login_path": null,
        "movie_extra": "",
        "movie_keywords": "{title} {year}",
        "movie_query": "EXTRA",
        "name": "LostFilm",
        "parser": {
            "infohash": "",
            "name": "item('a', order=2)",
            "peers": "item(tag='td', order=3)",
            "row": "find_once(tag='body').find_all('tr')",
            "seeds": "item(tag='td', order=2)",
            "size": "item(tag='td', order=5)",
            "torrent": "item(tag='a', attribute='href', order=2)"
        },
        "private": false,
        "season_extra": "",
        "season_extra2": "",
        "season_keywords": "{title:ru} Season {season:2}",
        "season_keywords2": "{title} Season{season}",
        "season_query": "EXTRA",
        "separator": "+",
        "show_query": "",
        "subpage": true,
        "tv_extra": "",
        "tv_extra2": "",
        "tv_keywords": "{title} s{season:2}e{episode:2}",
        "tv_keywords2": ""
    }
}
```

### Благодарности
- @scakemyer за написаный Quasar Burst модуль!
- @mancuniancol за его работу над Magnetic, этот аддон не появился без него.
- @elgatito за продолжения Quasar в Elementum.
- Ну и всем пользователям с XBMC.ru.
