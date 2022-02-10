import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:group',
                    args=[self.group.slug]): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[self.user.username]): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[self.post.id]): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=[self.post.id]): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test-slug',
            description='Тестовое описание',
        )
        for numbers in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {numbers}',
                group=cls.group,
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.guest_client = Client()
        cache.clear()

        self.pages_names = {
            'posts:group_list': self.group.slug,
            'posts:profile': self.user.username,
        }

    def test_first_page_contains_ten_records_in_index(self):
        """Первая страница в index содержит 10 постов"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_in_index(self):
        """Вторая страница в index содержит 3 поста"""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records_in_group_and_profile(self):
        """Первая страница в group и profile содержит 10 постов"""
        for adress, args in self.pages_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(reverse(adress, args=[args]))
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records_in_group_and_profile(self):
        """Вторая страница в group и profile содержит 3 поста"""
        for adress, args in self.pages_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(
                    reverse(adress, args=[args]) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.guest_client = Client()

    def test_pages_show_correct_context(self):
        """Шаблон posts:group сформирован с правильным контекстом."""
        templates_pages_name = {
            'posts:group': self.group.slug,
            'posts:profile': self.user.username,
        }
        for names, args in templates_pages_name.items():
            with self.subTest(names=names):
                response = self.guest_client.get(reverse(names, args=[args]))
                first_object = response.context['page_obj'][0]
                post_slug_0 = first_object.group.slug
                self.assertEqual(post_slug_0, 'test-slug')
                post_author_0 = first_object.author.username
                self.assertEqual(post_author_0, 'author')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон posts:post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('posts:post_detail', args=[self.post.id]))
        current_object = response.context['post']
        post_id = current_object.id
        self.assertEqual(post_id, self.post.id)

    def test_create_post_show_correct_context(self):
        """Шаблон post:post_create сформирован с правильным контекстом"""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон post:post_edit сформирован с правильным контекстом"""
        response = self.author_client.get(
            reverse('posts:post_edit', args=[self.post.id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                is_edit_field = response.context.get('is_edit')
                self.assertIsInstance(form_field, expected)
                self.assertEqual(is_edit_field, True)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageExistTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Yahsa1')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_post_with_image_exist(self):
        self.assertTrue(Post.objects.filter(image='posts/small.gif'))

    def test_index_show_correct_image_in_context(self):
        """В Шаблоне index картинка передается в словаре context"""
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        test_object = response.context['page_obj'][0]
        post_image = test_object.image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_detail_image_exist(self):
        """В шаблоне post_detail картинка передается в словаре context"""
        response = self.author_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        test_object = response.context['post']
        post_image = test_object.image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_and_profile_image_exist(self):
        """В шаблонах group и profile картинка передается в словаре context"""
        templates_pages_name = {
            'posts:group': self.group.slug,
            'posts:profile': self.user.username,
        }
        for names, args in templates_pages_name.items():
            with self.subTest(names=names):
                response = self.author_client.get(reverse(names, args=[args]))
                test_object = response.context['page_obj'][0]
                post_image = test_object.image
                self.assertEqual(post_image, 'posts/small.gif')


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)
        cls.author = User.objects.create_user(username='Yasha1')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

    def setUp(self):
        self.follow = Follow.objects.get_or_create(
            user=self.follower,
            author=self.author
        )

    def test_follow(self):
        """В базе создается объект follow и только один"""
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower.is_authenticated, author=self.author,
            ).exists()
        )
        response = Follow.objects.filter(
            user=self.follower.is_authenticated, author=self.author,
        ).count()
        self.assertEqual(response, 1)

    def test_unfollow(self):
        """После отписки объект follow удаляется из базы"""
        Follow.objects.filter(
            user=self.follower.is_authenticated, author=self.author,
        ).delete()
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower.is_authenticated, author=self.author,
            ).exists()
        )

    def test_follow_index_context(self):
        """Шаблон follow_index сформирован с правильным контекстом """
        response = self.follower_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        self.assertEqual = (post_author_0, 'author')
        post_text_0 = first_object.text
        self.assertEqual = (post_text_0, 'Тестовый текст')

    def test_follow_index_context_wo_author(self):
        """Шаблон follow_index после удаления подписки убирает посты автора"""
        Follow.objects.filter(
            user=self.follower.is_authenticated, author=self.author,
        ).delete()
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual = (len(response.context['page_obj']), 0)


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Yasha1')
        cls.commentator = User.objects.create_user(username='commentator')
        cls.commentator_client = Client()
        cls.commentator_client.force_login(cls.commentator)
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.commentator,
            text='Тестовый текст комментария'
        )

    def test_comment(self):
        """в базе создается объект comment и только один"""
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                author=self.commentator,
                text='Тестовый текст комментария'
            ).exists
        )
        response = Comment.objects.filter(
            post=self.post,
            author=self.commentator,
            text='Тестовый текст комментария'
        ).count()
        self.assertEqual(response, 1)

    def test_comment_context(self):
        """Шаблон post_detail сформирован с правильными комментариями"""
        response = self.commentator_client.get(
            reverse('posts:post_detail', args=[self.post.id]))
        comments = response.context['comments'][0]
        expected_fields = {
            comments.author.username: 'commentator',
            comments.post.id: self.post.id,
            comments.text: 'Тестовый текст комментария'
        }
        for fields, values in expected_fields.items():
            with self.subTest(expected_fields=expected_fields):
                self.assertEqual(fields, values)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Yasha1')
        cls.author_client = Client()
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

    def test_caching(self):
        """Проверка кеширования главной страницы"""
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        posts_count = Post.objects.count()
        self.post.delete
        self.assertEqual(len(response.context['page_obj']), posts_count)
        cache.clear()
        posts_count = Post.objects.count()
        self.assertEqual(len(response.context['page_obj']), posts_count)
