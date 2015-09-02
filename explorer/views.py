__author__ = '@jotegui'

from flask import render_template
from explorer import app

@app.route('/')
def main():
	"""Main page."""
	return render_template("index.html")
