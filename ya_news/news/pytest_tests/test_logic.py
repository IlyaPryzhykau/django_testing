import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(
        author_client, news_id_for_args, form_data
):
    """
    Тест: Авторизованный пользователь может создать
    комментарий к новости.
    """
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')

    assert Comment.objects.count() == 1

    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_id_for_args, form_data
):
    """Тест: Анонимный пользователь не может создать комментарий к новости."""
    url = reverse('news:detail', args=news_id_for_args)
    login_url = reverse('users:login')
    expected_redirect_url = f'{login_url}?next={url}'

    response = client.post(url, data=form_data)
    assertRedirects(response, expected_redirect_url)

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_use_bad_words(news_id_for_args, author_client):
    """
    Тест: Пользователь не может использовать запрещенные
    слова в комментарии.
    """
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_words_data)

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
        news_id_for_args, comment_id_for_args, author_client
):
    """Тест: Автор комментария может удалить свой комментарий."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(url)

    new_url = reverse('news:detail', args=news_id_for_args)
    assertRedirects(response, f'{new_url}#comments')

    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        comment_id_for_args, not_author_client
):
    """Тест: Пользователь не может удалить комментарий другого пользователя."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.post(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        comment_id_for_args, news_id_for_args, author_client, form_data
):
    """Тест: Пользователь может редактировать свой комментарий."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_data)

    new_url = reverse('news:detail', args=news_id_for_args)
    assertRedirects(response, f'{new_url}#comments')

    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        comment_id_for_args, news_id_for_args,
        not_author_client, form_data, comment
):
    """Тест: Пользователь может редактировать только свой комментарий."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
