from PIL import Image

from app.tests.base import TestCase
from app import db, app
from app.models import Category, Painting, Video, AdminUser
from config import BASE_DIR, THUMBNAIL_SIZE, THUMBNAIL_SIZE_LARGE

import os
import sys

class CategoryModel(TestCase):
    def test_slug(self):
        cat = Category(name="This is a test ---")
        self.assertEqual(cat.slug, "this-is-a-test")

    def test_autoincrement(self):
        self.createCategories(2)

        self.assertEqual(Category.query.get(1).id, 1)
        self.assertEqual(Category.query.get(2).id, 2)

class PaintingModel(TestCase):
    def test_relationship_to_category(self):
        cat = Category(name="test_cat")
        p = Painting(name="test_paint", category=cat, filename='')
        db.session.add(cat)
        db.session.add(p)
        db.session.commit()

        cat = Category.query.filter_by(name="test_cat").first()
        cats_painting = cat.paintings[0]
        p = Painting.query.filter_by(name="test_paint").first()
        self.assertEqual(cats_painting.name, p.name)
        self.assertEqual(p.category.name, cat.name)

    def test_user_inputs_file_with_not_unique_filename(self):
        p1 = Painting(name="test1", filename="test.jpg")
        db.session.add(p1)
        db.session.commit()
        p2 = Painting(name="test2", filename="test.jpg")
        db.session.add(p2)
        db.session.commit()

        p1 = Painting.query.get(1)
        p2 = Painting.query.get(2)
        self.assertNotEqual(p1.filename, p2.filename)

    def test_thumbnails_are_made_properly_for_wide_images(self):
        Painting.makeThumbnail(
            os.path.join(app.config['MEDIA_ROOT'], 'test_landscape_image.jpg'),
            os.path.join(app.config['MEDIA_ROOT'], 'test_landscape_thumb.jpg')
        )

        with open(os.path.join(app.config['MEDIA_ROOT'], 'test_landscape_thumb.jpg'), 'rb') as img_file:
            with Image.open(img_file) as landscape_thumb:
                _,_,width,height = landscape_thumb.getbbox()
                landscape_thumb.close()

                self.assertAlmostEqual(width, THUMBNAIL_SIZE, delta=1)
                self.assertAlmostEqual(height, THUMBNAIL_SIZE, delta=1)

    def test_thumbnails_are_made_properly_for_tall_images(self):
        Painting.makeThumbnail(
            os.path.join(app.config['MEDIA_ROOT'], 'test_portrait_image.jpg'),
            os.path.join(app.config['MEDIA_ROOT'], 'test_portrait_thumb.jpg')
        )

        with open(os.path.join(app.config['MEDIA_ROOT'], 'test_portrait_thumb.jpg'), 'rb') as img_file:
            with Image.open(img_file) as portrait_thumb:
                _,_,width,height = portrait_thumb.getbbox()
                portrait_thumb.close()

                self.assertAlmostEqual(width, THUMBNAIL_SIZE, delta=1)
                self.assertAlmostEqual(height, THUMBNAIL_SIZE, delta=1)

    def test_large_thumbnails_are_large(self):
        Painting.makeThumbnail(
            os.path.join(app.config['MEDIA_ROOT'], 'test_portrait_image.jpg'),
            os.path.join(app.config['MEDIA_ROOT'], 'test_portrait_thumb.jpg'),
            True
        )

        with open(os.path.join(app.config['MEDIA_ROOT'], 'test_portrait_thumb.jpg'), 'rb') as img_file:
            with Image.open(img_file) as portrait_thumb:
                _,_,width,height = portrait_thumb.getbbox()
                portrait_thumb.close()

                self.assertAlmostEqual(width, THUMBNAIL_SIZE_LARGE, delta=1)
                self.assertAlmostEqual(height, THUMBNAIL_SIZE_LARGE, delta=1)

    def test_category_order_autoincrements(self):
        self.createPaintings(3, category_name="cat")
        p = Painting.query.all()
        self.assertEqual(p[0].id, p[0].category_order)
        self.assertEqual(p[1].id, p[1].category_order)
        self.assertEqual(p[2].id, p[2].category_order)

class AdminUserModel(TestCase):
    def test_password_hash(self):
        u = AdminUser(username="testname", password="testpass")
        self.assertTrue(u.check_password('testpass'))
        self.assertFalse(u.check_password('incorrectpass'))
