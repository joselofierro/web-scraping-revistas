import argparse
import logging
logging.basicConfig(level=logging.INFO)
import pandas as pd
from article import Article
from base import engine,Base,Session
import sqlite3

logger = logging.getLogger(__name__)

def main(filename):
	# genera el esquima
	Base.metadata.create_all(engine)
	# generamos la session
	session = Session()
	articles = pd.read_csv(filename)

	for index,row in articles.iterrows():
		logging.info('loading article uid {} into db'.format(row['uid']))
		article = Article(row['uid'], row['body'], row['title'],
						   row['url'],row['newspaper_uid'], row['host'],
						   row['n_tokens_title'], row['n_tokens_body']
						)
		session.add(article)

	try:
		session.commit()
		session.close()
	except sqlite3.Error as e:
		logging.info('ERROR {}'.format(e))

	


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('filename', help='the file you want load into db', type=str)
	args = parser.parse_args()
	main(args.filename)
