import pytest

from django.test.client import Client
from django.urls import reverse

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, all_news):
    """
    Тест проверяет, что на главной странице
    отображается корректное количество новостей.
    """

    response = client.get(HOME_URL)
    news_count = response.context['object_list'].count()
    assert NEWS_COUNT_ON_HOME_PAGE == news_count


@pytest.mark.django_db
def test_news_order(client, all_news):
    """
    Тест проверяет, что новости на главной странице
    отсортированы по дате публикации (от новых к старым).
    """

    response = client.get(HOME_URL)
    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, ten_comments, news_id_for_args):
    """
    Тест проверяет, что комментарии к новости отсортированы
    по дате создания (от старых к новым).
    """

    detail_url = reverse('news:detail', args=news_id_for_args)
    response = client.get(detail_url)

    if 'comments' in response.context:
        comments_in_context = response.context['comments']
        all_timestamps = [comment.created for comment in comments_in_context]
        sorted_timestamps = sorted(all_timestamps)

        for comment in ten_comments:
            assert comment.created in all_timestamps

        assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, comment_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (Client(), False),
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('news:edit', pytest.lazy_fixture('comment_id_for_args'))
    )
)
def test_pages_contains_form_if_authorized(
        parametrized_client, comment_in_list, name, args
):
    """
    Тест проверяет, что форма для комментариев отображается
    только для авторизованных пользователей.
    """

    url = reverse(name, args=args)
    response = parametrized_client.get(url)

    if response.context is not None:
        if comment_in_list:
            assert 'form' in response.context
            assert isinstance(response.context['form'], CommentForm)
        else:
            assert 'form' not in response.context
    else:
        assert comment_in_list is False
