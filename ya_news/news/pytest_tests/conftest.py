import pytest

from django.test.client import Client
from django.utils import timezone

from datetime import timedelta

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def all_news():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def author_of_comment(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author_of_comment(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author_of_comment):
    client = Client()
    client.force_login(author_of_comment)
    return client


@pytest.fixture
def not_author_client(not_author_of_comment):
    client = Client()
    client.force_login(not_author_of_comment)
    return client


@pytest.fixture
def comment(author_of_comment, news):
    comment = Comment.objects.create(
        news=news,
        author=author_of_comment,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def ten_comments(author_of_comment, news):
    today = timezone.now()
    comments_list = [
        Comment.objects.create(
            news=news,
            author=author_of_comment,
            text=f'Текст комментария {index}',
            created=today - timedelta(days=index)
        )
        for index in range(10)
    ]
    return comments_list


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
