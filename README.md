# Netflix Database (Django + PostgreSQL)

## Датасет
Используется датасет **Netflix Movies and TV Shows** с Kaggle:  
https://www.kaggle.com/datasets/shivamb/netflix-shows

Файл датасета: `netflix_titles.csv`

---

## Структура базы данных
База данных нормализована до **третьей нормальной формы (3НФ)**.

Основные таблицы:
- `country`
- `title`
- `genre`
- `actor`
- `director`

Таблицы связей (M:N):
- `title_genre`
- `title_actor`
- `title_director`

Связь **1:N**:
- `country → title`

---

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
