import pytest

from django.test.client import Client
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


HOME_URL = reverse('news:home')

pytestmark = pytest.mark.django_db


def test_news_count(client, all_news):
    """
    Тест: Проверка, что на главной странице отображается
    корректное количество новостей.
    """
    response = client.get(HOME_URL)

    object_list = response.context.get('object_list')
    assert object_list is not None

    news_count = object_list.count()
    assert settings.NEWS_COUNT_ON_HOME_PAGE == news_count


def test_news_order(client, all_news):
    """
    Тест: Проверка, что новости на главной странице отсортированы по дате
    публикации (от новых к старым).
    """
    response = client.get(HOME_URL)

    object_list = response.context.get('object_list')
    assert object_list is not None

    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


def test_comments_order(client, ten_comments, news_id_for_args):
    """
    Тест: Проверка, что комментарии к новости отсортированы по дате
    создания (от старых к новым).
    """
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = client.get(detail_url)

    comments_in_context = response.context.get('comments')
    assert comments_in_context is not None

    all_timestamps = [comment.created for comment in comments_in_context]
    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('news:edit', pytest.lazy_fixture('comment_id_for_args'))
    )
)
def test_form_displayed_for_authorized_users(author_client, name, args):
    """
    Тест: Проверка, что форма для комментариев отображается
    для авторизованных пользователей.
    """
    url = reverse(name, args=args)
    response = author_client.get(url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('news:edit', pytest.lazy_fixture('comment_id_for_args'))
    )
)
def test_form_not_displayed_for_anonymous_users(client, name, args):
    """
    Тест: Проверка, что форма для комментариев не
    отображается для анонимных пользователей.
    """
    url = reverse(name, args=args)
    response = client.get(url)

    assert 'form' not in vars(response)
