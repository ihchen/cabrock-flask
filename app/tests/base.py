import os
import unittest

from config import BASE_DIR
from app import app, db
from app.models import Painting, Category

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
        app.config['MEDIA_ROOT'] = os.path.join(BASE_DIR, 'app', 'tests', 'testfiles')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def createCategories(self, num, **kwargs):
        for i in range(1, num+1):
            c = Category(name="cat_test_%d"%(i), **kwargs)
            db.session.add(c)
            db.session.commit()

    def createPaintings(self, num, **kwargs):
        for i in range(1, num+1):
            p = Painting(name="paint_test_%d"%(i), filename="test_%d.jpg"%(i), **kwargs)
            db.session.add(p)
            db.session.commit()
