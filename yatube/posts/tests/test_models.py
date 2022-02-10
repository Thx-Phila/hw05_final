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
