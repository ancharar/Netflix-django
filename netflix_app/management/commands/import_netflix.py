import csv
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from netflix_app.models import (
    Country, Title, Genre, Actor, Director,
    TitleGenre, TitleActor, TitleDirector
)


def norm(s: str) -> str:
    return " ".join(s.strip().split())


def split_list(s: str):
    if not s:
        return []
    return [norm(x) for x in s.split(",") if norm(x)]


def parse_date_added(s: str):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


class Command(BaseCommand):
    help = "Import Netflix titles from netflix_titles.csv into normalized tables."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to netflix_titles.csv")
        parser.add_argument("--limit", type=int, default=0, help="Limit rows (0 = all)")

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        limit = options["limit"]

        try:
            f = open(csv_path, "r", encoding="utf-8")
        except OSError as e:
            raise CommandError(f"Cannot open CSV: {e}")

        with f:
            reader = csv.DictReader(f)
            required_cols = {"title", "type", "release_year", "country", "listed_in", "cast", "director", "rating", "duration", "date_added"}
            missing = required_cols - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV missing columns: {sorted(missing)}")

            # Кэши, чтобы не дергать БД на каждую строку
            country_cache = {c.name: c for c in Country.objects.all()}
            genre_cache = {g.name: g for g in Genre.objects.all()}
            actor_cache = {a.full_name: a for a in Actor.objects.all()}
            director_cache = {d.full_name: d for d in Director.objects.all()}

            created_titles = 0
            processed = 0

            for row in reader:
                processed += 1
                if limit and processed > limit:
                    break

                title_name = norm(row.get("title", ""))
                if not title_name:
                    continue

                ttype = norm(row.get("type", ""))
                release_year_raw = norm(row.get("release_year", ""))
                try:
                    release_year = int(release_year_raw)
                except ValueError:
                    continue

                duration = norm(row.get("duration", "")) or None
                rating = norm(row.get("rating", "")) or None
                date_added = parse_date_added(row.get("date_added", ""))

                # country: в исходном CSV иногда несколько стран через запятую.
                # Для простой версии берем первую (чтобы 1:N не ломать)
                country_raw = row.get("country", "") or ""
                country_list = split_list(country_raw)
                country_obj = None
                if country_list:
                    c_name = country_list[0]
                    country_obj = country_cache.get(c_name)
                    if not country_obj:
                        country_obj = Country.objects.create(name=c_name)
                        country_cache[c_name] = country_obj

                # создаем Title
                title_obj = Title.objects.create(
                    name=title_name,
                    type=ttype,
                    release_year=release_year,
                    duration=duration,
                    rating=rating,
                    date_added=date_added,
                    country=country_obj,
                )
                created_titles += 1

                # genres
                for g_name in split_list(row.get("listed_in", "")):
                    g_obj = genre_cache.get(g_name)
                    if not g_obj:
                        g_obj = Genre.objects.create(name=g_name)
                        genre_cache[g_name] = g_obj
                    # не плодим дубликаты
                    TitleGenre.objects.get_or_create(title=title_obj, genre=g_obj)

                # actors
                for a_name in split_list(row.get("cast", "")):
                    a_obj = actor_cache.get(a_name)
                    if not a_obj:
                        a_obj = Actor.objects.create(full_name=a_name)
                        actor_cache[a_name] = a_obj
                    TitleActor.objects.get_or_create(title=title_obj, actor=a_obj)

                # directors
                for d_name in split_list(row.get("director", "")):
                    d_obj = director_cache.get(d_name)
                    if not d_obj:
                        d_obj = Director.objects.create(full_name=d_name)
                        director_cache[d_name] = d_obj
                    TitleDirector.objects.get_or_create(title=title_obj, director=d_obj)

            self.stdout.write(self.style.SUCCESS(
                f"Done. Processed rows: {processed}. Created titles: {created_titles}."
            ))
