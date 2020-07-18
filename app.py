#!/usr/bin/env python

from bs4 import BeautifulSoup
from dataclasses import dataclass
from dataclasses_serialization.json import JSONSerializer
from flask import Flask, request, Response
from typing import List

import urllib.request


class PypiRetriever():
	"""
	This object is used to retrieve informations from PyPI.org
	"""

	@staticmethod
	def get_versions(lib_name):
		# Retrieve the page content, */simple/* URL are easier to parse
		page_content = urllib.request.urlopen("https://pypi.org/simple/%s/" % lib_name)
		page_content_bytes = page_content.read()
		html_content = page_content_bytes.decode("utf8")
		page_content.close()

		# Load the HTML content in BeautifulSoup to parse it easily
		parsed_html_content = BeautifulSoup(html_content, features="lxml")
		ahrefs = parsed_html_content.body.find_all("a", href=True)

		# Iterate over the <a href="...">...</a> 
		lib_versions = []
		for ahref in ahrefs:
			# Get only the tar.gz files, no whl wanted
			if ahref.text.endswith("gz"):
				# Remove the last 7 chars (.tar.gz) and split on "-" to get the version number only
				version_id = ahref.text[:-7].split("-")[-1]

				lib_versions.append(version_id)
		return lib_versions


@dataclass
class LibraryData():
	"""
	Class that represents a library on PyPI with its different versions.
	"""
	name: str
	versions: List[str]
	counter: int = 0


# Init flask app
flask_app = Flask(__name__)

@flask_app.route("/libs/get/<lib_name>")
def get_lib(lib_name):
	"""
	Goal is to generate a json like: 
	{
	  "library":"flask",
	  "count":34
	  "versions": [...]
	}
	"""

	lib_versions = PypiRetriever.get_versions(lib_name)	
	lib = LibraryData(name=lib_name, versions=lib_versions, counter=len(lib_versions))

	return JSONSerializer.serialize(lib);


if __name__ == '__main__':
	flask_app.run(host='0.0.0.0')
