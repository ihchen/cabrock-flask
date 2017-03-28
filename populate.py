from app import db, models, app

import os

print('Adding categories...')
if models.Category.query.filter_by(name="Landscapes").count() == 0:
    c = models.Category(name="Landscapes")
    db.session.add(c)
    db.session.commit()
if models.Category.query.filter_by(name="Undergraduate Thesis").count() == 0:
    c = models.Category(name="Undergraduate Thesis", header='"Confronting the Killer"', description="Thesis Statement", thumbsize_large=True)
    db.session.add(c)
    db.session.commit()
if models.Category.query.filter_by(name="Miscellaneous").count() == 0:
    c = models.Category(name="Miscellaneous")
    db.session.add(c)
    db.session.commit()

print('Adding paintings...')
f = open('imageDetails.csv', 'r')
line = f.readline()
while line:
    details = line.split(', ')
    if models.Painting.query.filter_by(name=details[0]).count() == 0:
        category = models.Category.query.filter_by(name=details[1]).first()
        p = models.Painting(
            name=details[0],
            category=category,
            medium=details[2],
            dimensions=details[3],
            year=int(details[4]),
            filename="%s.jpg" % (details[0])
        )
        models.Painting.makeThumbnail(
            os.path.join(app.config['MEDIA_ROOT'], 'image', p.filename),
            os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', p.thumbname),
            category.thumbsize_large if category else False,
        )
        db.session.add(p)
        db.session.commit()
    line = f.readline()

print('Adding videos...')
urls = ['https://www.youtube.com/embed/eljkmV5MVhQ']
urls.append('https://www.youtube.com/embed/a07fccJJbNU')
for u in urls:
    if models.Video.query.filter_by(embed_url=u).count() == 0:
        v = models.Video(
            embed_url = u,
        )
        db.session.add(v)
        db.session.commit()

print('Adding Admin User...')
if models.AdminUser.query.get('jpsjqeyb') is None:
    u = models.AdminUser(username="jpsjqeyb", password="Gracie12")
    db.session.add(u)
    db.session.commit()
