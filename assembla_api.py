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
    """Make a PUT request to assembla,  currently expects globally defined variable X_API_KEY
    and X_API_SECRET to be defined (see ./config.ini). data is expected to be a json encode-able
    Python object.  Returns Python json decoded object or False if status code is greater than 200"""
    headers = { 'X-Api-Key' : X_API_KEY,
                'X-Api-Secret' : X_API_SECRET,
                'Content-type' : 'application/json'}
    r = requests.put("https://api.assembla.com" + url +".json", headers=headers, data=json.dumps(data))

    # Should be Error checking in here

    if r.status_code > 200:
        return False
    return json.loads(r.text)


def api_request(url):
    """Make a GET request to assembla,  currently expects globally defined variable X_API_KEY
    and X_API_SECRET to be defined (see ./config.ini). data is expected to be a json encode-able
    Python object.  Returns Python json decoded object or False if status code is greater than 200"""
    headers = { 'X-Api-Key' : X_API_KEY,
                'X-Api-Secret' : X_API_SECRET}
    r = requests.get("https://api.assembla.com" + url, headers=headers)
    # Should be Error checking in here
    if r.status_code > 200:
        return False
    return json.loads(r.text)



class Assembla_Space:
    """Implements a basic Assembla space model- this class basically just wraps calls to 
    api_request() to lazy load tickets, comments, documents, wiki_pages etc. Several functions
    impelemnt loops which manage the paging of large return sets (eg. spaces with more than 1000 tickets)
    """
    def __init__(self, name='', id='', status=0, wiki_name='', **kwargs):
        """Initializes an Assembla_Space object, expects to be passed name, id, status and wiki_name
        This is usually instantiated through the get_space function in the assembla_utils module.
        Its best to make a dict of space values and then pass the results into Assembla_Space with 
        variable unpacking such as:
    
        space_dict = api_request("/v1/spaces/" + id)      
        space = new Assembla_Space(**space_dict)

        The choice of requring name, id, status and wiki_name is driven by the __unicode__() 
        implementation.
        """
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
        """Updates the name of a space on Assembla"""
        ret = api_put("/v1/spaces/" + self.id, {"space" : { "name" : name }})
        if ret != False:
            self.name = name
        return ret

    def users(self):
        """Lazy load the users associated with this space"""
        if self._users == None:
            self._users = api_request("/v1/spaces/" + self.id + "/users.json")
        return self._users

    def user_roles(self):
        """Get the user roles defined for this space"""
        if self._user_roles == None:
            self._uesr_roles = api_request("/v1/spaces/" + self.id + "/user_roles.json")
        return self._user_roles

    def repos (self):
        """List any repositories assigned to this space"""
        if self._repos == None:
            self._repos = api_request("/v1/spaces/" + self.id + "/space_tools/repo.json")
        return self._repos

    # Shouldn't we be doing this with decorators or something?
    def milestones(self):
        """Get the space Milestones"""
        if self._milestones == None:
            self._milestones = api_request("/v1/spaces/" + self.id + "/milestones")
        return self._milestones

    def custom_fields(self):
        """Load the custom fields defined for the space"""
        if self._custom_fields == None:
            self._custom_fields = api_request("/v1/spaces/" + self.id + "/tickets/custom_fields")
        return self._custom_fields

    def ticket_components(self):
        """Get the set of possible ticket components defined for the space
        NOTE: Assembla has deprecated (without warning i might add) this field
        components may now be accessed through custom fields.
        """
        if self._ticket_components == None:
            self._ticket_components = api_request("/v1/spaces/" + self.id + "/ticket_components")
        return self._ticket_components


    def ticket_statuses(self):
        """Get the set of possible ticket status types defined for this space."""
        if self._ticket_statuses == None:
            self._ticket_statuses = api_request("/v1/spaces/" + self.id + "/tickets/statuses")
        return self._ticket_statuses

    def tickets(self, load_comments=False):
        """Lazy load tickets for the current space. This pages by sets of 100 making a seperate API 
        request for every 100 tickets. If load_comments is True ticket comments will be loaded as an
        attribute on each ticket. This can be very resource intensive. NOTE: if the api_request()
        never returns false (indicating that there are no additional tickets in the pager) then this
        will loop infinitely - arguably a poor design choice."
        """
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
        """Lazy load wiki_pages via paged calls to assembla. Note from help(Assembla_Spaces.tickets)
        applies here as well. 
        """
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
        """Lazy load documents via paged calls to assembla. Note from help(Assembla_Spaces.tickets)
        applies here as well. 
        """
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
        """Wrapper function that simply accesses (lazy loads) all space information. For performance
        reasons this does not include ticket comments.
        """
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

