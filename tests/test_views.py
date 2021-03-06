from test_plus.test import TestCase
from referrals import models
from django.contrib.auth import get_user_model


User = get_user_model()


class TestFlatReferralListView(TestCase):

    def setUp(self):
        referrer = self.make_user('u1')
        for _ in range(15):
            referred = self.make_user('u1{}'.format(_))
            models.FlatReferral.objects.create(
                referrer=referrer,
                referred=referred
            )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(self.reverse('referrals:flat_referral_list'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/referrals/flat-referrals/',
            fetch_redirect_response=False
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get('/referrals/flat-referrals/')
        self.assertEqual(
            resp.status_code,
            200
        )

    def test_view_url_accessible_by_name(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get(self.reverse('referrals:flat_referral_list'))
        self.assertEqual(
            resp.status_code,
            200
        )

    def test_view_uses_correct_template(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get(self.reverse('referrals:flat_referral_list'))
        self.assertEqual(
            resp.status_code,
            200
        )

        self.assertTemplateUsed(
            resp,
            'referrals/flat_referral_list.html'
        )

    def test_pagination_is_ten(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get(self.reverse('referrals:flat_referral_list'))
        self.assertEqual(
            resp.status_code,
            200
        )
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        self.assertTrue(len(resp.context['flat_referral_list']) == 10)

    def test_lists_all_referrals(self):
        self.client.login(username='u1', password='password')
        # Get second page and confirm it has (exactly) remaining 5 items
        resp = self.client.get(self.reverse(
            'referrals:flat_referral_list')+'?page=2')
        self.assertEqual(
            resp.status_code,
            200
        )
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        self.assertTrue(len(resp.context['flat_referral_list']) == 5)


class TestFlatReferralDetailView(TestCase):

    def setUp(self):
        referrer = self.make_user('u1')
        for _ in range(15):
            referred = self.make_user('u1{}'.format(_))
            models.FlatReferral.objects.create(
                referrer=referrer,
                referred=referred
            )

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(self.reverse(
            'referrals:flat_referral_detail', pk=1))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/referrals/flat-referrals/1/',
            fetch_redirect_response=False
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get('/referrals/flat-referrals/1/')
        self.assertEqual(
            resp.status_code,
            200
        )

    def test_view_url_accessible_by_name(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get(self.reverse(
            'referrals:flat_referral_detail', pk=1))
        self.assertEqual(
            resp.status_code,
            200
        )

    def test_view_uses_correct_template(self):
        self.client.login(username='u1', password='password')
        resp = self.client.get(self.reverse(
            'referrals:flat_referral_detail', pk=1))
        self.assertEqual(
            resp.status_code,
            200
        )

        self.assertTemplateUsed(resp, 'referrals/flat_referral_detail.html')

    def test_permission_denied(self):
        User.objects.create_user(
            username='fakeuser', password='password')
        self.client.login(username='fakeuser', password='password')
        resp = self.client.get(self.reverse(
            'referrals:flat_referral_detail', pk=1))
        self.assertEqual(
            resp.status_code,
            403
        )


class TestMultiLevelReferralListView(TestCase):

    def setUp(self):
        referrer = self.make_user('u1')

        self.root = models.MultiLevelReferral.add_root(user=referrer)
        _id = User.objects.last().id
        referred = self.make_user('u{}'.format(int(_id) + 1))
        self.root.add_child(user=referred)

        for _ in range(15):
            referral = models.MultiLevelReferral.objects.get(user=referred)
            _id = User.objects.last().id
            user = self.make_user('u{}'.format(int(_id) + 1))
            referral.add_child(user=user)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_list'))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/referrals/multi-level-referrals/',
            fetch_redirect_response=False
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get('/referrals/multi-level-referrals/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_list'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_list'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(
            resp, 'referrals/multi_level_referral_list.html')

    def test_pagination_is_ten(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['is_paginated'])
        self.assertEqual(
            len(resp.context['multi_level_referral_list']),
            10
        )

    def test_second_page(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_list') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['is_paginated'])
        self.assertEqual(
            len(resp.context['multi_level_referral_list']),
            6
        )


class TestMultiLevelReferralDetailView(TestCase):

    def setUp(self):
        referrer = self.make_user('u1')

        self.root = models.MultiLevelReferral.add_root(user=referrer)
        _id = User.objects.last().id
        referred = self.make_user('u{}'.format(int(_id + 1)))
        self.root.add_child(user=referred)

        for _ in range(15):
            referral = models.MultiLevelReferral.objects.get(user=referred)
            _id = User.objects.last().id
            user = self.make_user('u{}'.format(int(_id + 1)))
            referral.add_child(user=user)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_detail', pk=2))
        self.assertRedirects(
            resp,
            '/accounts/login/?next=/referrals/multi-level-referrals/2/',
            fetch_redirect_response=False
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get('/referrals/multi-level-referrals/2/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_detail', pk=2))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(
            username='{}'.format(self.root.user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_detail', pk=2))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(
            resp, 'referrals/multi_level_referral_detail.html')

    def test_permission_denied(self):
        user = User.objects.create_user(
            username='fakeuser', password='password')
        self.root.add_child(user=user)

        self.client.login(
            username='{}'.format(user.username),
            password='password'
        )
        resp = self.client.get(self.reverse(
            'referrals:multi_level_referral_detail', pk=2))
        self.assertEqual(
            resp.status_code,
            403
        )


class TestJavaScriptCode(TestCase):

    def setUp(self):
        self.user = self.make_user()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/referrals/')
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(
            resp.context['default_value'],
            'TEST'
        )
        self.assertEqual(
            resp.context['prefix'],
            ''
        )

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(self.reverse('referrals:javascript_code'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.context['default_value'],
            'TEST'
        )
        self.assertEqual(
            resp.context['prefix'],
            ''
        )
