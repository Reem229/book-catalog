from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import BookCatalog, Base, Book, User

engine = create_engine('sqlite:///bookscatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Reem Mohammed", email="rr@yahoo.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Create dummy book catalog
bookcatalog1 = BookCatalog(user_id='1', name='History')
session.add(bookcatalog1)
session.commit()

bookcatalog2 = BookCatalog(user_id='1', name='Fiction')
session.add(bookcatalog2)
session.commit()

bookcatalog3 = BookCatalog(user_id='1', name='Classics')
session.add(bookcatalog3)
session.commit()

#{'name':'Someone Like Me','author':' ','pages':' pages','pic' :'', 'id':'3'}
# Create books
book1 = Book(user_id=1, name="The Alchemist", author="Paulo Coelho",
                 pages="197", picture="https://images.gr-assets.com/books/1483412266l/865.jpg",
                 bookcatalog=bookcatalog3)

session.add(book1)
session.commit()

book2 = Book(user_id=1, name="A Christmas Carol", author="Charles Dickens",
                 pages="104", picture="https://images.gr-assets.com/books/1406512317l/5326.jpg",
                 bookcatalog=bookcatalog3)
session.add(book2)
session.commit()

book3 = Book(user_id=1, name="Someone Like Me", author="M.R. Carey",
                 pages="500", picture="https://images.gr-assets.com/books/1518797001l/37975580.jpg",
                 bookcatalog=bookcatalog2)
session.add(book3)
session.commit()

book4 = Book(user_id=1, name="The Shadows We Hide", author="Allen Eskens",
                 pages="352", picture="https://images.gr-assets.com/books/1522081435l/39088549.jpg",
                 bookcatalog=bookcatalog2)

session.add(book4)
session.commit()

print "added menu items!"
