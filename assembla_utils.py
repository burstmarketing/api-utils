from __future__ import print_function
from bs4 import BeautifulSoup
from assembla_api import Assembla_Space, api_request

import requests
import sys
import os
import pickle
import time

import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

# You're right,  these shouldn't be global,  or even in here
username = config.get("Assembla", "build_username")
password = config.get("Assembla", "build_password")


#######################
## Functions for scraping/pickling assembla space information
##


def scrape_and_pickle(space_ids):
    for id in space_ids:
        print("Scraping %s " % (id), end='')
        sys.stdout.flush()
        start = time.time()

        s = get_space(id)

        print("(%s) " % (s.name[0:40]), end='' )
        print("%s" % ("." * (40 - len(s.name))), end='')
        sys.stdout.flush()


        s.load_all()
        pickle.dump(s, open("pickles/" + s.id + ".pickle", "w"))

        t = time.time() - start
        print(" Done (%f)" % t)
    return True


def pickled_spaces():
    spaces = os.listdir("pickles/")
    for id in spaces:
        with open("pickles/" + id, "r") as f:
            yield pickle.load(f)



########################
## Function used to prefix space names
##
## Note: to_traffic was a dict containing 
## "Space Name" : "space-id" key/values
##

def prefix_spaces_for_transition():
    for id in get_space_ids():
        space = get_space(id)
        if space.id in to_traffic.values():
            space.update_name("[To Traffic] - " + space.name)
        else:
            space.update_name("[To Exit] - " + space.name)

######################
## Space and User utility functions
##

def get_space(id):
    space_dict = api_request("/v1/spaces/" + id )
    return Assembla_Space(**space_dict)


def get_space_ids():
    s = requests.session()

    r = s.get("https://burstmarketing.assembla.com/p/home")

    soup = BeautifulSoup(r.text)
    auth = soup.findAll(attrs={"name" : "authenticity_token"})[0]['value']

    payload = { 'user[login]' : username,
                'user[password]' : password,
                'utf8' : '',
                'authenticity_token' : auth,
                'protfolio_id' : 'burstmarketing',
                'commit' : 'Login' }

    r = s.post('https://burstmarketing.assembla.com/do_login', data=payload)

    r = s.get('https://burstmarketing.assembla.com/p/projects')
    soup = BeautifulSoup(r.text)

    ids = [x['data-space-id'] for x in soup.findAll(attrs={"data-space-id"  : True} )]
    return ids



def get_users():
    s = requests.session()

    r = s.get("https://burstmarketing.assembla.com/p/home")

    soup = BeautifulSoup(r.text)
    auth = soup.findAll(attrs={"name" : "authenticity_token"})[0]['value']

    payload = { 'user[login]' : username,
                'user[password]' : password,
                'utf8' : '',
                'authenticity_token' : auth,
                'protfolio_id' : 'burstmarketing',
                'commit' : 'Login' }

    r = s.post('https://burstmarketing.assembla.com/do_login', data=payload)

    r = s.get('https://burstmarketing.assembla.com/p/users')
    soup = BeautifulSoup(r.text)

    ret = []
    for tr in soup.findAll("tr", {"id" : re.compile("u-*") }):
        id = tr['id']
        user_name = tr.find("td", {"class" : "user_role-id"}).contents[2].strip(" \t\r\n()")
        common_name = tr.find("a").string
        ret.append( (id, user_name, common_name))

    # [(x['id'], x.find("td", {"class" : "user_role-id"}).contents[2].strip() ) for x in soup.findAll("tr", {"id" : re.compile("u-*") } )]
    return ret
