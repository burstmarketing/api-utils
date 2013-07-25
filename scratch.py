from traffic_api import TrafficAPI, jobs_summary
from assembla_api import Assembla_Space
from assembla_utils import *
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

USER_NAME = config.get("TrafficLive", "use
API_TOKEN = config.get("TrafficLive", "api
                                          
traffic = TrafficAPI(USER_NAME, API_TOKEN)




# Example - Traffic API
# USER_NAME = config.get("TrafficLive", "username")
# API_TOKEN = config.get("TrafficLive", "api_token")
# 
# traffic = TrafficAPI(USER_NAME, API_TOKEN)
# 
# j = traffic._get( "job/309093" )
# jd = traffic._get("jobdetail/" + str(j['jobDetailId']))
# jt = copy.deepcopy(j['jobTasks'][0])

##
# Example - Space scrape
# s_ids = get_space_ids()
# scrape_and_pickle(s_ids[:3])
# spaces = [s for s in pickled_spaces]
#











