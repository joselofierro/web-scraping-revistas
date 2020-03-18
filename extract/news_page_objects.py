from common import config
import requests
import bs4


# clase con codigo auxiliar
class NewsPage:

	def __init__(self, news_site_uuid, url):
		self._config = config()['news_sites'][news_site_uuid]
		self._queries = self._config['queries']
		self._html = None
		self._url = url
		self._visit(url)

	# funcion con informacion del documento que se parsea
	def _select(self, query_string):
		return self._html.select(query_string)

	# metodo que visita la pagina
	def _visit(self, url):
		# peticion get a la url
		rsp = requests.get(url)
		# status de la respuesta
		rsp.raise_for_status()

		# arbol de nodos
		self._html = bs4.BeautifulSoup(rsp.text, 'html.parser')




# clase que va a representar la pagina principal de la web
class HomePage(NewsPage):

	def __init__(self, news_site_uuid, url):
		super().__init__(news_site_uuid, url)

	@property
	def article_links(self):
		link_list = []

		for link in self._select(self._queries['homepage_articles_links']):
			if link and link.has_attr('href'):
				link_list.append(link)

		# creamos una tupla sin liks repetidos
		return set(link['href'] for link in link_list)
	


# clase con el cuerpo y titulo de la noticia
class ArticlePage(NewsPage):

	def __init__(self, news_site_uuid, url):
		super().__init__(news_site_uuid, url)



	@property
	def url(self):
		return self._url
	
	@property
	def body(self):
		result = self._select(self._queries['article_body'])
		return result[0].text if len(result) > 0 else ''

	@property
	def title(self):
		result = self._select(self._queries['article_title'])
		return result[0].text if len(result) > 0 else ''
	
	
