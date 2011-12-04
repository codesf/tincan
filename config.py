import web
import private_conf

# water hydrant project -  https://github.com/chiuki/drop2drink/blob/master/hydrant.py
# public version https://www.google.com/fusiontables/DataSource?dsrcid=2335280

SERVER = "http://www.codesf.org:8080"

#db = web.database(host='', dbn="mysql", db='', user='', pw='')
web.config.debug = True
