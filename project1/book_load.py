import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

def main():
    # Check for environment variable
    if not os.getenv('DATABASE_URL'):
        raise RuntimeError('DATABASE_URL is not set')

    # Set up database
    engine = create_engine(os.getenv('DATABASE_URL'))
    db = scoped_session(sessionmaker(bind=engine))
    with open('books.csv') as csv_file:
        f = csv.reader(csv_file)

        query = text('INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year);')

        # get rid of first line (headers)
        _=next(f)
        for isbn, title, author, year in f:
            db.execute(query, {'isbn': isbn, 'title': title, 'author':author, 'year':year})
            print(f'added {isbn}, {title}, {author}, {year}')

        db.commit()

if __name__ == '__main__':
    main()
