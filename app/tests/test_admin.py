from flask import url_for
from PIL import Image
from io import BytesIO

from app.tests.base import TestCase
from app.models import Painting, Category, AdminUser, Video, About
from app import db, app
from config import MEDIA_ROOT, BASE_DIR

import os
import sys

class AdminSortable(TestCase):
    def test_ajax_request_old_lt_new_for_paintings(self):
        self.createPaintings(3)

        # Move p1 to the back
        self.app.post('/update/paintings/order', data=dict(
            oldIndex="0",
            newIndex="2"
        ))

        p = Painting.query.order_by(Painting.filename)
        self.assertEqual(p[0].id, 3)
        self.assertEqual(p[1].id, 1)
        self.assertEqual(p[2].id, 2)

    def test_ajax_request_old_gt_new_for_paintings(self):
        self.createPaintings(3)

        # Move p1 to the back
        self.app.post('/update/paintings/order', data=dict(
            oldIndex="2",
            newIndex="0"
        ))

        p = Painting.query.order_by(Painting.filename)
        self.assertEqual(p[0].id, 2)
        self.assertEqual(p[1].id, 3)
        self.assertEqual(p[2].id, 1)

    def test_ajax_request_old_lt_new_for_categories(self):
        self.createCategories(1)
        cat = Category.query.get(1)
        self.createPaintings(3, category=cat)

        self.app.post('/update/paintings/%s/order'%(cat.slug), data=dict(
            oldIndex="0",
            newIndex="2"
        ))

        p = Painting.query.order_by(Painting.filename)
        self.assertEqual(p[0].category_order, 3)
        self.assertEqual(p[1].category_order, 1)
        self.assertEqual(p[2].category_order, 2)

    def test_ajax_request_new_lt_old_for_categories(self):
        self.createCategories(1)
        cat = Category.query.get(1)
        self.createPaintings(3, category=cat)

        self.app.post('/update/paintings/%s/order'%(cat.slug), data=dict(
            oldIndex="2",
            newIndex="0"
        ))

        p = Painting.query.order_by(Painting.filename)
        self.assertEqual(p[0].category_order, 2)
        self.assertEqual(p[1].category_order, 3)
        self.assertEqual(p[2].category_order, 1)

class AdminLogin(TestCase):
    def test_admin_login_page_has_form(self):
        response = self.app.get("/admin/login")
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)
        self.assertIn(b'form', response.data)

    def test_admin_correct_login(self):
        u = AdminUser(username="testname", password="testpass")
        db.session.add(u)
        db.session.commit()

        response = self.app.post('/admin/login', data=dict(
            username="testname",
            password="testpass"
        ), follow_redirects=True)

        self.assertIn(b'Carly A. Brock', response.data)

    def test_admin_incorrect_password_login(self):
        u = AdminUser(username="testname", password="testpass")
        db.session.add(u)
        db.session.commit()

        response = self.app.post('/admin/login', data=dict(
            username="testname",
            password="incorrectpass"
        ), follow_redirects=True)

        self.assertIn(b'Incorrect password', response.data)

    def test_admin_incorrect_username_login(self):
        u = AdminUser(username="testname", password="testpass")
        db.session.add(u)
        db.session.commit()

        response = self.app.post('/admin/login', data=dict(
            username="incorrecttestname",
            password="incorrectpass"
        ), follow_redirects=True)

        self.assertIn(b'Incorrect username', response.data)

class AdminEdit(TestCase):
    def test_ajax_request_update_painting_details(self):
        p = Painting(name="test1", medium="m1", dimensions="d1", year="y1", filename="test1.jpg")
        db.session.add(p)
        db.session.commit()

        self.app.post('/update/paintings/details', data=dict(
            filename="test1.jpg",
            name="test2",
            medium="m2",
            dimensions="d2",
            year="y2"
        ))

        p = Painting.query.filter_by(filename="test1.jpg").first()
        self.assertEqual(p.name, "test2")
        self.assertEqual(p.medium, "m2")
        self.assertEqual(p.dimensions, "d2")
        self.assertEqual(p.year, "y2")

    def test_ajax_edit_category_details(self):
        self.createCategories(1)
        self.app.post('/update/categories/details', data=dict(
            id='cat_test_1',
            name='new_name',
            header='header',
            description='descr',
        ))
        c = Category.query.get(1)
        self.assertEqual(c.name, 'new_name')
        self.assertEqual(c.description, 'descr')

    def test_ajax_edit_category_updates_foreign_key_relation(self):
        self.createCategories(1)
        c = Category.query.get(1)
        db.session.add(Painting(name="tp", filename='', category=c))
        db.session.commit()
        self.app.post('/update/categories/details', data=dict(
            id='cat_test_1',
            name='new_name',
            header='',
            description='descr',
        ))
        self.assertEqual(Painting.query.get(1).category_name, 'new_name')

    def test_ajax_edit_category_changes_thumbnail_sizes(self):
        with open(os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', 'test.thumbnail.jpg'), 'rb') as img_file:
            with Image.open(img_file) as thumb:
                large = thumb.getbbox()[2] > 200
        c = Category(name="testcat", thumbsize_large=large)
        db.session.add(c)
        db.session.commit()
        p = Painting(name="test", filename="test.jpg", category=Category.query.get(1))
        db.session.add(p)
        db.session.commit()

        self.app.post('/update/categories/details', data=dict(
            id='testcat',
            name='new+',
            header='head+',
            description='',
            thumbsize=None if large else 'large'
        ))

        with open(os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', 'test.thumbnail.jpg'), 'rb') as img_file:
            with Image.open(img_file) as thumb:
                if large:
                    self.assertLess(thumb.getbbox()[2], 200)
                else:
                    self.assertGreater(thumb.getbbox()[2], 200)

    def test_ajax_edit_video_details(self):
        db.session.add(Video(name="testvid", embed_url="testurl.com"))
        db.session.commit()
        self.app.post('/update/videos/details', data=dict(
            oldurl="testurl.com",
            name="newvid",
            embedurl="newvidurl.com"
        ))
        v = Video.query.get(1)
        self.assertEqual(v.name, 'newvid')
        self.assertEqual(v.embed_url, 'newvidurl.com')

class AdminDelete(TestCase):
    def test_ajax_request_delete_painting(self):
        self.createPaintings(2)

        self.app.post('/update/paintings/delete', data=dict(
            filename="test_2.jpg"
        ))

        self.assertEqual(Painting.query.count(), 1)

    def test_ajax_request_deleting_item_from_db_lowers_ids_by_one(self):
        self.createPaintings(3)

        self.app.post('/update/paintings/delete', data=dict(
            filename="test_1.jpg"
        ))

        p2 = Painting.query.filter_by(filename="test_2.jpg").first()
        p3 = Painting.query.filter_by(filename="test_3.jpg").first()
        self.assertEqual(p2.id, 1)
        self.assertEqual(p3.id, 2)

    def test_lowering_max_id_sets_changes_autoincrement_value(self):
        self.createPaintings(3)
        db.session.delete(Painting.query.get(1))
        db.session.commit()
        Painting.query.get(2).id = 1
        db.session.commit()
        Painting.query.get(3).id = 2
        db.session.commit()
        self.createPaintings(1)
        self.assertEqual(Painting.query.filter_by(filename="test_1.jpg").first().id, 3)

    def test_deleting_painting_deletes_files(self):
        self.createPaintings(1)
        self.app.post('/update/paintings/delete', data=dict(
            filename="test_1.jpg"
        ))
        self.assertFalse(os.path.isfile(os.path.join(app.config['MEDIA_ROOT'], 'image', 'test_1.jpg')))
        self.assertFalse(os.path.isfile(os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', 'test_1.thumbnail.jpg')))

    def test_deleting_category(self):
        self.createCategories(1)
        self.app.post('/update/categories/delete', data=dict(
            name="cat_test_1",
            currentURL=""
        ))
        self.assertEqual(Category.query.count(), 0)

    def test_deleting_category_decrements_ids(self):
        self.createCategories(3)
        self.app.post('/update/categories/delete', data=dict(
            name="cat_test_1",
            curentURL=""
        ))
        c = Category.query.all()
        self.assertEqual(c[0].id, 1)
        self.assertEqual(c[1].id, 2)

    def test_deleting_video(self):
        db.session.add(Video(embed_url="test1.com"))
        db.session.commit()
        self.app.post('/update/videos/delete', data=dict(
            url="test1.com"
        ))
        self.assertEqual(Video.query.count(), 0)


class AdminUpload(TestCase):
    def test_upload_painting_creates_files(self):
        with open(os.path.join(app.config['MEDIA_ROOT'], 'test_landscape_image.jpg'), 'rb') as test:
            imgBytesIO = BytesIO(test.read())

        self.app.post('/update/paintings/new', data=dict(
            {'file': (imgBytesIO, 'test_1.jpg')},
            name="test",
            category="",
            medium="",
            dimensions="",
            year="",
        ))

        self.assertTrue(os.path.isfile(os.path.join(app.config['MEDIA_ROOT'], 'image', 'test_1.jpg')))
        self.assertTrue(os.path.isfile(os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', 'test_1.thumbnail.jpg')))

    def test_upload_painting_updates_database(self):
        self.createCategories(1)

        with open(os.path.join(app.config['MEDIA_ROOT'], 'test_landscape_image.jpg'), 'rb') as test:
            imgBytesIO = BytesIO(test.read())

        self.app.post('/update/paintings/new', data=dict(
            {'file': (imgBytesIO, 'test_1.jpg')},
            name="test",
            category="cat_test_1",
            medium="med",
            dimensions="dim",
            year="yr",
        ))

        p = Painting.query.filter_by(name="test").first()
        self.assertNotEqual(p.category, None)
        self.assertEqual(p.category, Category.query.get(1))
        self.assertEqual(p.filename, "test_1.jpg")
        self.assertEqual(p.year, "yr")

    def test_adding_category_adds_to_database(self):
        self.app.post('/update/categories/new', data=dict(
            name="new_cat",
            header="",
            description="",
            thumbsize="",
        ))
        self.assertEqual(Category.query.count(), 1)

    def test_adding_category_with_large_thumbnail_size(self):
        self.app.post('/update/categories/new', data=dict(
            name="new_cat",
            header="",
            description="",
            thumbsize="large"
        ))
        c = Category.query.get(1)
        self.assertTrue(c.thumbsize_large)

    def test_adding_category_redirects_to_new_category_page(self):
        response = self.app.post('/update/categories/new', data=dict(
            name="new_cat",
            header="header",
            description=""
        ), follow_redirects=True)
        self.assertIn(b'header', response.data)

    def test_adding_category_with_used_name_fails(self):
        self.createCategories(1)
        response = self.app.post('/update/categories/new', data=dict(
            name="cat_test_1",
            header="headerre",
            description="",
            currentURL="/contact"
        ), follow_redirects=True)
        self.assertIn(b'carlybrockart@gmail.com', response.data)
        self.assertEqual(Category.query.count(), 1)

    def test_adding_video(self):
        self.app.post('/update/videos/new', data=dict(
            name="",
            embedurl="test.com"
        ))
        self.assertEqual(Video.query.count(), 1)

class AdminAbout(TestCase):
    def test_about_edit_quote(self):
        db.session.add(About(description="d", quote="q", quotee="qe"))
        db.session.commit()

        self.app.post('/update/about/details', data=dict(
            component="quote",
            content="quizzy"
        ))

        self.assertEqual(About.query.get(1).quote, "quizzy");

    def test_about_edit_quotee(self):
        db.session.add(About(description="d", quote="q", quotee="qe"))
        db.session.commit()

        self.app.post('/update/about/details', data=dict(
            component="quotee",
            content="qui"
        ))

        self.assertEqual(About.query.get(1).quotee, "qui");

    def test_about_edit_description(self):
        db.session.add(About(description="d", quote="q", quotee="qe"))
        db.session.commit()

        self.app.post('/update/about/details', data=dict(
            component="description",
            content="diefine"
        ))

        self.assertEqual(About.query.get(1).description, "diefine");
