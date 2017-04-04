from app.tests.base import TestCase
from app import mail, db
from app.models import Category,Painting,Video,About

class Header(TestCase):
    def test_adding_category_adds_to_navigation_menu(self):
        self.createCategories(1)
        response = self.app.get('/')
        self.assertIn(bytes(Category.query.get(1).name, encoding='utf-8'), response.data)

    def test_categories_sorted_by_id_in_navigation_menu(self):
        self.createCategories(2)

        response = self.app.get('/')
        cat1 = Category.query.get(1)
        cat2 = Category.query.get(2)
        cat1index = response.data.find(bytes(cat1.name, 'utf-8'))
        cat2index = response.data.find(bytes(cat2.name, 'utf-8'))
        self.assertLess(cat1index, cat2index)

        cat1.id = -1
        cat2.id = -2
        db.session.commit()
        cat2.id = 1
        cat1.id = 2
        db.session.commit()

        response = self.app.get('/')
        cat1index = response.data.find(bytes(cat1.name, 'utf-8'))
        cat2index = response.data.find(bytes(cat2.name, 'utf-8'))
        self.assertLess(cat2index, cat1index)

class PaintingsView(TestCase):
    def test_adding_painting_adds_to_paintings_page(self):
        p = Painting(name="name", medium="medium", dimensions="dimensions", year="12345", filename="test.jpg")
        db.session.add(p)
        db.session.commit()

        response = self.app.get('/paintings/')
        self.assertIn(b"name", response.data)
        self.assertIn(b"medium", response.data)
        self.assertIn(b"dimensions", response.data)
        self.assertIn(b"12345", response.data)
        self.assertIn(b'test.jpg', response.data)

    def test_paintings_ordered_by_id(self):
        self.createPaintings(2)

        response = self.app.get('/paintings/')
        p1 = Painting.query.get(1)
        p2 = Painting.query.get(2)
        p1Index = response.data.find(bytes(p1.name,'utf-8'))
        p2Index = response.data.find(bytes(p2.name,'utf-8'))
        self.assertLess(p1Index, p2Index)

        p1.id = -1
        p2.id = -2
        db.session.commit()
        p1.id = 2
        p2.id = 1
        db.session.commit()

        response = self.app.get('/paintings/')
        p1Index = response.data.find(bytes(p1.name,'utf-8'))
        p2Index = response.data.find(bytes(p2.name,'utf-8'))
        self.assertLess(p2Index, p1Index)

    def test_category_view_that_does_not_exist_displays_message(self):
        response = self.app.get('/paintings/dne')
        self.assertIn(b"The page you were looking for does not exist.", response.data)

    def test_paintings_view_with_no_category_displays_correct_title(self):
        response = self.app.get('/paintings/')
        self.assertIn(b'Paintings', response.data)

    def test_category_name_appears_in_categorys_view(self):
        c = Category(name="testname")
        db.session.add(c)
        db.session.commit()

        response = self.app.get('/paintings/testname')
        self.assertIn(b'testname', response.data)

    def test_category_description_appears(self):
        c = Category(name="testname", description="testdescription")
        db.session.add(c)
        db.session.commit()

        response = self.app.get('/paintings/testname')
        self.assertIn(b'testdescription', response.data)

    def test_category_header_appears(self):
        c = Category(name="testname", header="testheader")
        db.session.add(c)
        db.session.commit()

        response = self.app.get('/paintings/testname')
        self.assertIn(b'testheader', response.data)

    def test_category_with_large_thumbnails(self):
        c = Category(name='testname', thumbsize_large=True)
        db.session.add(c)
        db.session.commit()
        c = Category.query.get(1)
        p = Painting(name='testpaint', category=c, filename='test.jpg')

        response = self.app.get('/paintings/testname')
        self.assertIn(b'thumbnail-large', response.data)

    def test_category_ordering_works(self):
        c = Category(name='testcat')
        db.session.add(c)
        db.session.commit()
        c = Category.query.get(1)
        p1 = Painting(name='paint1', category=c, category_order=2, filename='test.jpg')
        db.session.add(p1)
        db.session.commit()
        p2 = Painting(name='paint2', category=c, category_order=1, filename='test.jpg')
        db.session.add(p2)
        db.session.commit()

        response = self.app.get('/paintings/testcat')
        p1Index = response.data.find(bytes(Painting.query.get(1).name, 'utf-8'))
        p2Index = response.data.find(bytes(Painting.query.get(2).name, 'utf-8'))
        self.assertLess(p2Index, p1Index)

class VideosView(TestCase):
    def test_adding_video_adds_to_video_page(self):
        v = Video(embed_url="test/embed/test")
        db.session.add(v)
        db.session.commit()

        response = self.app.get('/videos')
        v = Video.query.get(1)
        self.assertIn(bytes(v.embed_url, 'utf-8'), response.data)

    def test_videos_ordered_by_id(self):
        v1 = Video(embed_url="test1")
        db.session.add(v1)
        db.session.commit()
        v2 = Video(embed_url="test2")
        db.session.add(v2)
        db.session.commit()

        response = self.app.get('/videos')
        v1 = Video.query.get(1)
        v2 = Video.query.get(2)
        v1Index = response.data.find(b'test1')
        v2Index = response.data.find(b'test2')
        self.assertLess(v1Index, v2Index)

        v1.id = -1
        v2.id = -2
        db.session.commit()
        v1.id = 2
        v2.id = 1
        db.session.commit()

        response = self.app.get('/videos')
        v1Index = response.data.find(b'test1')
        v2Index = response.data.find(b'test2')
        self.assertLess(v2Index, v1Index)

class ContactView(TestCase):
    def test_email_is_sent(self):
        with mail.record_messages() as outbox:
            self.app.post('/contact', data=dict(
                name='testname',
                email='test@email.com',
                subject='testsubject',
                message='testmessage',
            ))

            self.assertEqual(len(outbox), 1)
            self.assertEqual(outbox[0].subject, "testsubject")

    def test_success_message_appears_on_send(self):
        response = self.app.post('/contact', data=dict(
            name='testname',
            email='test@email.com',
            subject='testsubject',
            message='testmessage',
        ), follow_redirects=True)

        self.assertIn(b"Email successfully delivered", response.data)

class AboutView(TestCase):
    def test_about_model_details_appear_in_view(self):
        a = About(description="about me!", quote="awesome quote", quotee="coolguy")
        db.session.add(a)
        db.session.commit()

        response = self.app.get('/about/')
        self.assertIn(b'about me!', response.data)
        self.assertIn(b'awesome quote', response.data)
        self.assertIn(b'coolguy', response.data)
