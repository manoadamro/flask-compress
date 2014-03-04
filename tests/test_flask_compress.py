import unittest
import os

from flask import Flask, render_template

from flask.ext.compress import Compress


class DefaultsTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True

        Compress(self.app)

    def test_mimetypes_default(self):
        """ Tests COMPRESS_MIMETYPES default value is correctly set. """
        defaults = ['text/html', 'text/css', 'text/xml', 'application/json',
                    'application/javascript']
        self.assertEquals(self.app.config['COMPRESS_MIMETYPES'], defaults)

    def test_debug_default(self):
        """ Tests COMPRESS_DEBUG default value is correctly set. """
        self.assertEquals(self.app.config['COMPRESS_DEBUG'], False)

    def test_level_default(self):
        """ Tests COMPRESS_LEVEL default value is correctly set. """
        self.assertEquals(self.app.config['COMPRESS_LEVEL'], 6)

    def test_min_size_default(self):
        """ Tests COMPRESS_MIN_SIZE default value is correctly set. """
        self.assertEquals(self.app.config['COMPRESS_MIN_SIZE'], 500)


class UrlTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True

        small_path = os.path.join(os.getcwd(), 'tests', 'templates',
                                  'small.html')

        large_path = os.path.join(os.getcwd(), 'tests', 'templates',
                                  'large.html')

        self.small_size = os.path.getsize(small_path) - 1
        self.large_size = os.path.getsize(large_path) - 1

        Compress(self.app)

        @self.app.route('/small/')
        def small():
            return render_template('small.html')

        @self.app.route('/large/')
        def large():
            return render_template('large.html')

    def client_get(self, ufs):
        client = self.app.test_client()
        response = client.get(ufs, headers=[('Accept-Encoding', 'gzip')])
        self.assertEqual(response.status_code, 200)
        return response

    def test_compress_vary_header(self):
        """ Tests Vary header doesn't get overwritten. """
        test_value = 'test'

        client = self.app.test_client()
        headers = [('Accept-Encoding', 'gzip'), ('Vary', test_value)]
        response = client.get('/large/', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn(test_value, response.headers['Vary'])

    def test_compress_debug(self):
        """ Tests COMPRESS_DEBUG correctly affects response data. """
        self.app.debug = True

        self.app.config['COMPRESS_DEBUG'] = True
        response = self.client_get('/large/')
        self.assertNotEqual(self.large_size, len(response.data))

        self.app.config['COMPRESS_DEBUG'] = False
        response = self.client_get('/large/')
        self.assertEqual(self.large_size, len(response.data))

    def test_compress_level(self):
        """ Tests COMPRESS_LEVEL correctly affects response data. """
        self.app.config['COMPRESS_LEVEL'] = 1
        response = self.client_get('/large/')
        response1_size = len(response.data)

        self.app.config['COMPRESS_LEVEL'] = 6
        response = self.client_get('/large/')
        response6_size = len(response.data)

        self.assertNotEqual(response1_size, response6_size)

    def test_compress_min_size(self):
        """ Tests COMPRESS_MIN_SIZE correctly affects response data. """
        response = self.client_get('/small/')
        self.assertEqual(self.small_size, len(response.data))

        response = self.client_get('/large/')
        self.assertNotEqual(self.large_size, len(response.data))


if __name__ == '__main__':
    unittest.main()
