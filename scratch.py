from traffic_api import TrafficAPI, jobs_summary
from assembla_api import Assembla_Space
from assembla_utils import *
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

USER_NAME = config.get("TrafficLive", "username")
API_TOKEN = config.get("TrafficLive", "api_token")
                                          
traffic = TrafficAPI(USER_NAME, API_TOKEN)

# u'(R) Deep Flue Stove & Chimney',
client_id = '111442'


def paged(window_size):
    """This decorator ensures that any response that is returned by the 
    API is the complete response by looping through the response until the
    number of responses is less than the window_size variable"""
    def paged_decorator(func):
        def paged_wrapper(*args):

            current_window_length = window_size
            page = 1
            ret = []
            
            while current_window_length == window_size:
                items = func(*args, options = { 'windowSize' : '%s' % window_size,
                                                'currentPage' : '%s' % page})
                
                ret.extend(items)

                page += 1
                current_window_length = len(items)
                
            return ret

        return paged_wrapper
    return paged_decorator


# See: http://support.sohnar.com/entries/22982116-API-Filtering-by-Criteria
# For more information about how to use API filter Criteria
@paged(window_size = 20)
def get_client_projects(api, client_id, options = {}):
    """Get all the projects associated with a particular client id"""
    options['filter'] = 'clientCRMEntryId|EQ|%s' % client_id
    return api.projects(options)

@paged(window_size = 20)
def get_project_jobDetails(api, project_id, options = {}):
    """Get all the jobDetails for a particular project_id"""
    options['filter'] = 'ownerProjectId|EQ|%s' % project_id
    return api.jobdetails(options)

def get_client_jobDetails(api, client_id):
    """Get all the jobDetails for a particular client id"""
    project_ids = [p['id'] for p in get_client_projects(api, client_id)]
    return [jd for pid in project_ids for jd in get_project_jobDetails(api, pid)]

get_client_jobDetails(traffic, client_id)

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











