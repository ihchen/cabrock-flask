from app import models, db

models.Painting.query.delete()
print('Paintings deleted')
models.Category.query.delete()
print('Categories deleted')
models.Video.query.delete()
print('Videos deleted')
db.session.commit()
