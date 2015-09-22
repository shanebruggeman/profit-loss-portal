from app import db
from models import BlogPost

#create the database and the tables
db.create_all()

#insert
db.session.add(BlogPost("Good", "I\'m good."))
db.session.add(BlogPost("Good", "I\'m well."))

# commit the changes
db.session.commit()