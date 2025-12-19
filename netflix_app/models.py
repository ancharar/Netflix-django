from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "country"

    def __str__(self):
        return self.name


class Title(models.Model):
    MOVIE = "Movie"
    TV_SHOW = "TV Show"
    TYPE_CHOICES = [(MOVIE, "Movie"), (TV_SHOW, "TV Show")]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    release_year = models.IntegerField()
    duration = models.CharField(max_length=50, null=True, blank=True)
    rating = models.CharField(max_length=20, null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)

    country = models.ForeignKey(
        Country, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="titles"
    )

    class Meta:
        db_table = "title"
        indexes = [
            models.Index(fields=["release_year"]),
            models.Index(fields=["type"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.release_year})"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "genre"

    def __str__(self):
        return self.name


class Actor(models.Model):
    full_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "actor"

    def __str__(self):
        return self.full_name


class Director(models.Model):
    full_name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "director"

    def __str__(self):
        return self.full_name


class TitleGenre(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = "title_genre"
        constraints = [
            models.UniqueConstraint(fields=["title", "genre"], name="uq_title_genre")
        ]


class TitleActor(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        db_table = "title_actor"
        constraints = [
            models.UniqueConstraint(fields=["title", "actor"], name="uq_title_actor")
        ]


class TitleDirector(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    director = models.ForeignKey(Director, on_delete=models.CASCADE)

    class Meta:
        db_table = "title_director"
        constraints = [
            models.UniqueConstraint(fields=["title", "director"], name="uq_title_director")
        ]

