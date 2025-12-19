from django.shortcuts import render
from django.db.models import Count

from netflix_app.models import (
    Country, Title, Genre, Actor, Director,
    TitleGenre, TitleActor, TitleDirector
)

def index(request):
    countries = Country.objects.all().order_by("id")[:30]
    genres = Genre.objects.all().order_by("id")[:30]
    actors = Actor.objects.all().order_by("id")[:30]
    directors = Director.objects.all().order_by("id")[:30]
    titles = Title.objects.select_related("country").all().order_by("id")[:30]

    title_genres = TitleGenre.objects.select_related("title", "genre").all().order_by("id")[:30]
    title_actors = TitleActor.objects.select_related("title", "actor").all().order_by("id")[:30]
    title_directors = TitleDirector.objects.select_related("title", "director").all().order_by("id")[:30]

    titles_by_country = (
        Country.objects.annotate(cnt=Count("titles")).order_by("-cnt", "name")[:10]
    )
    titles_by_year = (
        Title.objects.values("release_year").annotate(cnt=Count("id")).order_by("-cnt", "-release_year")[:10]
    )
    top_genres = (
        Genre.objects.annotate(cnt=Count("titlegenre")).order_by("-cnt", "name")[:10]
    )
    top_actors = (
        Actor.objects.annotate(cnt=Count("titleactor")).order_by("-cnt", "full_name")[:10]
    )

    ctx = {
        "page_title": "Netflix Database",
        "page_subtitle": "Таблицы отношений + статистика (Jinja2 макросы)",

        "rows_countries": [(c.id, c.name) for c in countries],
        "rows_genres": [(g.id, g.name) for g in genres],
        "rows_actors": [(a.id, a.full_name) for a in actors],
        "rows_directors": [(d.id, d.full_name) for d in directors],

        "rows_titles": [
            (t.id, t.name, t.type, t.release_year, (t.country.name if t.country else ""))
            for t in titles
        ],

        "rows_title_genres": [
            (tg.id, tg.title.name, tg.genre.name)
            for tg in title_genres
        ],
        "rows_title_actors": [
            (ta.id, ta.title.name, ta.actor.full_name)
            for ta in title_actors
        ],
        "rows_title_directors": [
            (td.id, td.title.name, td.director.full_name)
            for td in title_directors
        ],

        "rows_titles_by_country": [(c.name, c.cnt) for c in titles_by_country],
        "rows_titles_by_year": [(y["release_year"], y["cnt"]) for y in titles_by_year],
        "rows_top_genres": [(g.name, g.cnt) for g in top_genres],
        "rows_top_actors": [(a.full_name, a.cnt) for a in top_actors],
    }

    return render(request, "index.jinja", ctx, using="jinja2")
