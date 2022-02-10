from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.user = User.objects.create_user(username='Yahsa1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_urls_exists_at_desired_location(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location(self):
        """Страницы видны любому пользователю"""
        urls_dict = {
            'posts:group': self.group.slug,
            'posts:profile': self.user.username,
            'posts:post_detail': self.post.id,
        }
        for urls, args in urls_dict.items():
            with self.subTest(args=args):
                response = self.guest_client.get(reverse(urls, args=[args]))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create видна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location_anonymous(self):
        """Страница /create/ перенаправит неавторизованного пользователя"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница posts/<int:post_id>/edit видна автору поста"""
        response = self.author_client.get(
            reverse('posts:post_edit', args=[self.post.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_anonymous(self):
        """Страница posts/<int:post_id>/edit/ перенаправит"""
        """неавторизованного пользователя"""
        response = self.guest_client.get(
            reverse('posts:post_edit', args=[self.post.id]), follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_unknown_page(self):
        """страница /unknown_page вернет ошибку 404"""
        response = self.guest_client.get('/unknown_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адресс использует соответствующий шаблон"""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/testslug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_add_comment_url_exists_at_desired_location_anonymous(self):
        """Страница posts/<int:post_id>/comment перенаправит"""
        """неавторизованного пользователя"""
        response = self.guest_client.get(
            reverse('posts:add_comment', args=[self.post.id]), follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment')
