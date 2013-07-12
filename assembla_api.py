from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import re
import json
import sys

import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

username = config.get("Assembla", "build_username")
password = config.get("Assembla", "build_password")

X_API_KEY = config.get("Assembla", "X-Api-Key")
X_API_SECRET = config.get("Assembla", "X-Api-Secret")


def api_put(url, data):
    headers = { 'X-Api-Key' : X_API_KEY,
                'X-Api-Secret' : X_API_SECRET,
                'Content-type' : 'application/json'}
    r = requests.put("https://api.assembla.com" + url +".json", headers=headers, data=json.dumps(data))
    # Should be Error checking in here

    if r.status_code > 200:
        return False
    return json.loads(r.text)


def api_request(url):
    headers = { 'X-Api-Key' : X_API_KEY,
                'X-Api-Secret' : X_API_SECRET}
    r = requests.get("https://api.assembla.com" + url, headers=headers)
    # Should be Error checking in here
    if r.status_code > 200:
        return False
    return json.loads(r.text)



class Assembla_Space:
    def __init__(self, name='', id='', status=0, wiki_name='', **kwargs):
        self.name = name
        self.id = id
        self.status = status
        self.wiki_name = wiki_name

        self._tickets = None
        self._ticket_statuses = None
        self._custom_fields = None
        self._milestones = None
        self._ticket_components = None
        self._users = None
        self._user_roles = None
        self._repos = None
        self._wiki_pages = None
        self._documents = None

    def __unicode__(self):
        return u"<Space( '%s', '%s', '%s' )>" % (self.name, self.id, self.status)

    def __str__(self):      # tries to "look nice"
        return unicode(self).encode(sys.stdout.encoding or 'UTF-8','replace')

    def __repr__(self):     # must be unambiguous
        return repr(unicode(self))

    def update_name(self, name):
        ret = api_put("/v1/spaces/" + self.id, {"space" : { "name" : name }})
        if ret != False:
            self.name = name
        return ret

    def users(self):
        if self._users == None:
            self._users = api_request("/v1/spaces/" + self.id + "/users.json")
        return self._users

    def user_roles(self):
        if self._user_roles == None:
            self._uesr_roles = api_request("/v1/spaces/" + self.id + "/user_roles.json")
        return self._user_roles

    def repos (self):
        if self._repos == None:
            self._repos = api_request("/v1/spaces/" + self.id + "/space_tools/repo.json")
        return self._repos

    # Shouldn't we be doing this with decorators or something?
    def milestones(self):
        if self._milestones == None:
            self._milestones = api_request("/v1/spaces/" + self.id + "/milestones")
        return self._milestones

    def custom_fields(self):
        if self._custom_fields == None:
            self._custom_fields = api_request("/v1/spaces/" + self.id + "/tickets/custom_fields")
        return self._custom_fields

    def ticket_components(self):
        if self._ticket_components == None:
            self._ticket_components = api_request("/v1/spaces/" + self.id + "/ticket_components")
        return self._ticket_components


    def ticket_statuses(self):
        if self._ticket_statuses == None:
            self._ticket_statuses = api_request("/v1/spaces/" + self.id + "/tickets/statuses")
        return self._ticket_statuses

    def tickets(self, load_comments=False):
        if self._tickets == None:
            i = 1;
            self._tickets = []
            while( True ):
                ticks = api_request("/v1/spaces/%s/tickets.json?report=0&page=%i&per_page=100" % (self.id, i) )
                if ticks == False:
                    break
                self._tickets = self._tickets + ticks
                i = i + 1

            if load_comments:
                for ind,tick in enumerate(self._tickets):
                    self._tickets[ind]['comments'] = api_request("/v1/spaces/%s/tickets/%d/ticket_comments" % (self.id, tick['number']) )

        return self._tickets



    def wiki_pages(self):
        if self._wiki_pages == None:
            i =1;
            self._wiki_pages = []
            while (True):
                wikis = api_request("/v1/spaces/%s/wiki_pages.json?page=%i&per_page=25" % (self.id, i))
                if wikis == False:
                    break
                self._wiki_pages = self._wiki_pages + wikis
                i = i + 1
        return self._wiki_pages

    def documents(self):
        if self._documents == None:
            i = 1;
            self._documents = []
            while (True):
                docs = api_request("/v1/spaces/%s/documents.json?page=%i&per_page=100" % (self.id, i))
                if docs == False:
                    break
                self._documents = self._documents + docs
                i = i + 1
        return self._documents


    def load_all(self):
        self.tickets()
        self.users()
        self.user_roles()
        self.ticket_statuses()
        self.ticket_components()
        self.milestones()
        self.repos()
        self.custom_fields()
        self.wiki_pages()
        self.documents()
        return True




#############

