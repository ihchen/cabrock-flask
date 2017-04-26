from flask import url_for

from app.tests.base import TestCase
from app.models import Painting, Category, AdminUser, Video, About
from app import db, app
from config import MEDIA_ROOT, BASE_DIR

import os
import sys

class FixingAdminProblemsInitiallyIgnored(TestCase):
    def test_edit_category_unique_constraint(self):
        self.createCategories(2)

        self.app.post('/update/categories/details', data=dict(
            id = 'cat_test_2',
            name = 'cat_test_1',
            header = '',
            description = ''
        ))

        self.assertEqual(Category.query.filter_by(name='cat_test_2').count(), 1)

    def test_edit_category_pass_old_name_as_name(self):
        self.createCategories(1)

        self.app.post('/update/categories/details', data=dict(
            id = 'cat_test_1',
            name = 'cat_test_1',
            header = '',
            description = ''
        ))

        self.assertEqual(Category.query.filter_by(name='cat_test_1').count(), 1)

    def test_add_category_with_slug_already_taken(self):
        self.createCategories(1)

        self.app.post('/update/categories/new', data=dict(
            name = 'cat test 1',
            header = '',
            description = ''
        ))

        self.assertEqual(Category.query.filter_by(slug='cat-test-1-0').count(), 1)

        self.app.post('/update/categories/new', data=dict(
            name = 'cat-test-1',
            header = '',
            description = ''
        ))

        self.assertEqual(Category.query.filter_by(slug='cat-test-1-1').count(), 1)
