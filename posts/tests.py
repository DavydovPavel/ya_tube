
from unittest import TestCase
from django.test import Client, TestCase
from django.urls import reverse
from .models import Post, Group
from django.contrib.auth.models import User
from django.core.cache import cache

    
class AuthDefaultTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.not_auth = Client()
        self.test_user = User.objects.create_user(username = 'sarah', password = '12345')
        self.test_user2 = User.objects.create_user(username = 'terminator', password = '54321')
        self.test_group = Group.objects.create(title = 'Volodya', slug='vova', description='blablablb')                
        self.test_text = 'No future for you'
        self.test_text_changed = 'Daskolkojmojno?'
        self.client.force_login(self.test_user)
        
    def test_not_auth_create_new_post_or_comment(self):
        '''
         We verify that the Unauthorized visitor cannot post or comment the post 
        (redirects it to the login page)
        '''
        response = self.not_auth.get(reverse('new_post'), follow = True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

        self.post = Post.objects.create(text = 'No future for you', author= self.test_user, group=self.test_group)
        
        response = self.not_auth.get(reverse('add_comment', kwargs={'username': self.test_user.username, 'post_id':self.post.id}))
        self.assertRedirects(response, '/auth/login/?next=/sarah/1/comment')

    def test_create_profile_and_page_404(self):
        '''
        We check that after user registration, his personal page (profile) is created.
        '''
        response = self.client.get(reverse('profile', kwargs={'username': self.test_user.username}))
        self.assertEqual(response.status_code, 200)
               
        response = self.not_auth.get(reverse('profile', kwargs={'username': self.test_user.username}))
        self.assertEqual(response.status_code, 200)
        
        response = self.not_auth.get(reverse('profile', kwargs={'username': 'Va'}))
        self.assertEqual(response.status_code, 404)
        
    def test_auth_create_post_views_with_image(self):
        '''
        We check that after the publication of the post with image, 
        a new entry appears on the main page of the site (index), on the group(group_posts) page,
        on the user's personal page (profile), and on a separate page of the post (post).
        '''
        with open('./media/posts/image.png', 'rb') as img:  
            response = self.client.post(reverse('new_post'), {'text':self.test_text, 'group':self.test_group.id, 'image': img}, follow=True) 
                
        response = self.client.get(reverse ('post', kwargs={'username': self.test_user.username, 'post_id':1})) 
        self.assertContains(response, 'No future for you')
        self.assertContains(response, 'img')

        response = self.client.get(reverse('index'))
        self.assertContains(response, 'No future for you')
        self.assertContains(response, 'img')

        response = self.client.get(reverse ('profile', kwargs={'username': self.test_user.username}))
        self.assertContains(response, 'No future for you')
        self.assertContains(response, 'img')

        response = self.client.get(reverse ('group_posts', kwargs={'slug': self.test_group.slug}))
        self.assertContains(response, 'No future for you')
        self.assertContains(response, 'img')
        
        self.assertEqual(Post.objects.count(), 1)
        
    def test_edit_post(self):
        self.post = Post.objects.create(text = 'No future for you', author= self.test_user, group=self.test_group)
        
        response = self.client.post(reverse('post_edit', kwargs={'username': self.test_user.username, 'post_id':self.post.id}), data={'group':self.test_group.id, 'text': self.test_text_changed}, follow= True)
        self.client.post(reverse ('post_edit', kwargs={'username': self.test_user.username, 'post_id':self.post.id}), data={'group':self.test_group.id, 'text': self.test_text_changed}, follow= True)
        
        response = self.client.get(reverse ('post', kwargs={'username': self.test_user.username, 'post_id':self.post.id}))
        self.assertContains(response, self.test_text_changed)

        cache.clear()

        response = self.client.get(reverse('index'))
        self.assertContains(response, self.test_text_changed)

        response = self.client.get(reverse ('profile', kwargs={'username': self.test_user.username}))
        self.assertContains(response, self.test_text_changed)

        response = self.client.get(reverse ('post', kwargs={'username': self.test_user.username, 'post_id':self.post.id}))
        self.assertContains(response, self.test_text_changed)

        response = self.client.get(reverse ('group_posts', kwargs={'slug': self.test_group.slug}))
        self.assertContains(response, 'Daskolkojmojno?')

        self.assertEqual(Post.objects.count(), 1)

    def test_not_image_upload(self):
        with open('./media/posts/image.txt', 'rb') as img:
            response = self.client.post(reverse('new_post'), {'text':self.test_text, 'group':self.test_group.id, 'image': img}, follow=True)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'img')

    def test_follow_unfollow(self):
        with open('./media/posts/image.png', 'rb') as img:  
            response = self.client.post(reverse('new_post'), {'text':self.test_text, 'group':self.test_group.id, 'image': img}, follow=True) 
        self.client.force_login(self.test_user2)
        response = self.client.post(reverse ('profile_follow', kwargs={'username': self.test_user.username}))
        self.assertEqual(self.test_user.following.all().count(), 1)
        
        response = self.client.get(reverse ('follow_index'))
        self.assertContains(response, 'No future for you')

        response = self.client.post(reverse ('profile_unfollow', kwargs={'username': self.test_user.username}))
        self.assertEqual(self.test_user.following.all().count(), 0)

        cache.clear()

        response = self.client.get(reverse ('follow_index'))
        self.assertNotContains(response, 'self.test_text')