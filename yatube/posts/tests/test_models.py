from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у моделей post корректно работает __str__."""
        post = PostModelTest.post
        expected_post_text = post.text[:15]
        self.assertEqual(expected_post_text, str(post))

    def test_post_models_have_correct_verbose_name(self):
        """Проверяем, что у всех полей модели Post верный verbose_name"""
        field_verbose_name = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
        }
        post = PostModelTest.post
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_models_have_correct_help_text(self):
        """Проверяем, что у всех полей модели Post верный help_text"""
        field_help_text = {
            'text': 'Введите текст',
            'pub_date': 'Введите дату публикации',
            'group': 'Введите название группы',
            'author': 'Введите автора'
        }
        post = PostModelTest.post
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='test-slug',
            description='Тестовое описание группы',
        )

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у моделей group корректно работает __str__."""
        group = GroupModelTest.group
        expected_group_title = group.title[:15]
        self.assertEqual(expected_group_title, str(group))

    def test_group_models_have_correct_verbose_name(self):
        """Проверяем, что у всех полей модели Group верный verbose_name"""
        field_verbose_name = {
            'title': 'Заголовок',
            'slug': 'Уникальная строка',
            'description': 'Описание',
        }
        group = GroupModelTest.group
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_group_models_have_correct_help_text(self):
        """Проверяем, что у всех полей модели Post верный help_text"""
        field_help_text = {
            'title': 'Введите заголовок',
            'slug': 'Введите уникальную строку',
            'description': 'Введите описание',
        }
        group = GroupModelTest.group
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Yasha1')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый текст комментария',
        )

    def test_comment_models_have_correct_object_names(self):
        """Проверяем, что у моделей comment корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_comment_text = comment.text[:15]
        self.assertEqual(expected_comment_text, str(comment))

    def test_comment_models_have_correct_verbose_name(self):
        """Проверяем, что у всех полей модели Post верный verbose_name"""
        field_verbose_name = {
            'post': 'Пост, к которому прикрепляется комментарий',
            'text': 'Текст',
            'author': 'Автор',
        }
        comment = CommentModelTest.comment
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_models_have_correct_help_text(self):
        """Проверяем, что у всех полей модели Post верный help_text"""
        field_help_text = {
            'post': 'Укажите пост',
            'text': 'Введите текст',
            'author': 'Введите автора'
        }
        comment = CommentModelTest.comment
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='follower')
        cls.follow = Follow.objects.create(user=cls.user, author=cls.author)

    def test_follow_models_have_correct_object_names(self):
        """Проверяем, что у моделей follow корректно работает __str__."""
        follow = FollowModelTest.follow
        expected_user_username = follow.user.username
        self.assertEqual(expected_user_username, str(follow.user.username))
        expected_author_username = follow.author.username
        self.assertEqual(expected_author_username, str(follow.author.username))

    def test_follow_models_have_correct_verbose_name(self):
        """Проверяем, что у всех полей модели Follow верный verbose_name"""
        field_verbose_name = {
            'user': 'Пользователь',
            'author': 'Автор',
        }
        follow = FollowModelTest.follow
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_follow_models_have_correct_help_text(self):
        """Проверяем, что у всех полей модели Post верный help_text"""
        field_help_text = {
            'user': 'Укажите подписчика',
            'author': 'Укажите автора'
        }
        follow = FollowModelTest.follow
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).help_text, expected_value)
