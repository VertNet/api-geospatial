__author__ = '@jotegui'

from flask import render_template
from explorer import app

from google.appengine.api import modules

@app.route('/')
def main():
	"""Main page."""
	api_url = modules.get_hostname(module="api")
	return render_template("index.html", api_url=api_url)
