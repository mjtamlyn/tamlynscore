import json

from django.contrib import messages
from django.core.urlresolvers import reverse

from .factories import UserFactory


class ViewCase(object):
    user = None

    def _pre_setup(self):
        messages.outbox = []
        super(ViewCase, self)._pre_setup()

    def login(self, user=None, superuser=False):
        if user is None:
            user = self.user
        if user is None:
            self.user = UserFactory.create(is_superuser=superuser)
            user = self.user
        if self.user is None:
            self.user = user
        self.client.login(username=user.email, password=user.plain_password)

    def get_url(self):
        return reverse(self.url_name, kwargs=self.get_url_kwargs())

    def get_url_kwargs(self):
        return {}

    def generic_response(self, method, data={}, **kwargs):
        if 'is_ajax' in kwargs:
            kwargs.pop('is_ajax')
            kwargs['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        method = getattr(self.client, method)
        return method(self.get_url(), data=data, **kwargs)

    def get_response(self, data={}, **kwargs):
        return self.generic_response('get', data=data, **kwargs)

    def post_response(self, data={}, **kwargs):
        return self.generic_response('post', data=data, **kwargs)

    def put_response(self, data={}, **kwargs):
        return self.generic_response('put', data=data, **kwargs)

    def delete_response(self, data={}, **kwargs):
        return self.generic_response('delete', data=data, **kwargs)

    def json_post_response(self, data={}, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('is_ajax', True)
        response = self.post_response(data=json.dumps(data), **kwargs)
        response.json = json.loads(response.content)
        return response

    def json_put_response(self, data={}, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('is_ajax', True)
        response = self.put_response(data=json.dumps(data), **kwargs)
        response.json = json.loads(response.content)
        return response

    def json_delete_response(self, data={}, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('is_ajax', True)
        response = self.delete_response(data=json.dumps(data), **kwargs)
        response.json = json.loads(response.content)
        return response


class LoggedInViewCase(ViewCase):

    def generic_response(self, method, **kwargs):
        self.login()
        return super(LoggedInViewCase, self).generic_response(method, **kwargs)

    def test_auth(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
