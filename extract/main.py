# libreria para crear un script ejecutable
import argparse
import csv
# modulo logging para mostrar en consola reemplaza el print
import logging
# regular expresions
import re
#modulo con la configuracion inicial
from common import config
# clases con las funcionalidades del scraper
from news_page_objects import *
from datetime import datetime
# errores
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
# regular expresions 
is_well_formed_link = re.compile(r'^https?://.+/.+') # https://example.com/hello
is_root_path = re.compile(r'^/.+$') # /example

# funcion privado
def _news_scraper(news_site_uuid):
	host = config()['news_sites'][news_site_uuid]['url']
	logging.info('Beggining scraper for {}'.format(host))
	logging.info('finding links in homepage')
	homepage = HomePage(news_site_uuid, host)

	# vamos a recorrer cada vinculo que encontramos en la pagina principal
	articles = []
	for link in homepage.article_links:
		article = _fetch_article(news_site_uuid, host, link)

		if article:
			logger.info('Article fetched!')
			articles.append(article)
			print(article.title)

	# guardamos los articulos en csv
	_save_articles(news_site_uuid, articles)




def _save_articles(news_site_uuid, articles):

	#saber el dia de hoy
	now = datetime.now().strftime('%Y_%m_%d')
	#nombre de nuestro archivo
	file_name = '{}_{}_articles.csv'.format(news_site_uuid, now)

	# header del csv con propiedades que no empiezen con _
	headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))

	print(headers)

	# archivo en modo escritura si no esta lo crea
	with open(file_name, 'w+') as f:
		# vamos a escribir en las filas los headers
		writer = csv.writer(f)
		writer.writerow(headers)

		# por cada articulo lo escribimos en el archivo
		for article in articles:
			row = [ str(getattr(article, prop)) for prop in headers]
			writer.writerow(row)




# funcion que va a traer los articulos
def _fetch_article(news_site_uuid, host, link):
	logger.info('Start fetching article at {}'.format(link))

	article = None

	try:
		article = ArticlePage(news_site_uuid, _build_link(host, link))
	except (HTTPError, MaxRetryError) as e:
		logger.warning('Error while fetching article!', exc_info=False)

	if article and not article.body:
		logger.warning('Invalid article. There is not body')
		return None

	return article

# funcion que va a contruir el link con expressions regulars
def _build_link(host, link):

	if is_well_formed_link.match(link):
		return link

	elif is_root_path.match(link):
		return '{}{}'.format(host, link)

	else:
		return '{}/{}'.format(host, link) 


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	news_site_choices = list(config()['news_sites'].keys())
	parser.add_argument(
		    'news_site', 
			help='The new site that you want to scrape',
			type=str,
			choices=news_site_choices
		)

	# parseamos los argumentos
	args = parser.parse_args()
	_news_scraper(args.news_site)