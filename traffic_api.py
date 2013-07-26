from requests.auth import HTTPBasicAuth
import requests
import json

class TrafficAPI():
    def __init__(self, username, api_token):
        """Initialize a TrafficAPI object with username and api_token. username should 
        be the same user name used to login to traffic live,  the api_token can be 
        generated through the traffic live admin for the particular user. Usually this
        will come out of the config.ini Eg:
        
        USER_NAME = config.get("TrafficLive", "username")
        API_TOKEN = config.get("TrafficLive", "api_token")
        
        traffic = TrafficAPI(USER_NAME, API_TOKEN)
        """
        self.username = username
        self.api_token = api_token
        
                        
        self.base_url = "https://sohnar-prod.apigee.net/TrafficLiteServer/openapi/"
        self.headers = {"Accept" : "application/json"}
        
        self.max_attempts = 10
        
        # Store the last request made for later inspection/debugging
        self._last_request = None
        
        # Store the last response from _get(), _put(), _post() etc
        self._last_response = None
    
    def _get(self,resource, options={}):
        """ Make a GET call out to the Traffic API, resource is the uri of the API resource you wish to
        query. Options should be a key-value dict of url paramaters defined in the API documentation
        (usually paging etc). While developing this it was found to be somewhat faulty- occationally 
        needing multiple calls to the same resource to actually get data back. This means we make calls
        until self.max_attempts is reached and only break on a successful status_code.
        """
        attempts = 0
        url = self.base_url + resource

        # add "options" key/values as get params  
        if len(options.items()):
            url = url + "?" + '&'.join([key+"="+value for key,value in options.items()])

        while True:
            self._last_request = requests.get( url, headers=self.headers, auth=HTTPBasicAuth(self.username, self.api_token))

            if self._last_request.status_code <= 200:
                break;

            if attempts == self.max_attempts:
                raise Exception("Max attempts reached!")
            attempts = attempts + 1

        return json.loads(self._last_request.text)

    def clients(self,options={}):
        """Get a list of clients from the API"""
        self._last_response = self._get("crm/client", options)
        return self._last_response['resultList']


    def projects(self,options={}):
        """Get a list of projects from the API"""
        self._last_response = self._get("project", options)
        return self._last_response['resultList']

    def jobs(self,options={}):
        """Get a list of Jobs from the API"""
        self._last_response = self._get("job", options)
        return self._last_response['resultList']

    def jobdetails(self,options={}):
        """Get a list of JobDetails from the API"""
        self._last_response = self._get("jobdetail", options)
        return self._last_response['resultList']


    def _put(self, resource, payload):
        """Make a PUT request out to an API uri defined by resource. 
        payload should be a python object that can be json encoded and
        matches what the resource expectes as defined by the API documentation
        """
        self.headers['Content-type'] = "application/json"
        self.headers['Accept'] = "application/json"

        self._last_request = requests.put(self.base_url + resource, headers=self.headers, auth=HTTPBasicAuth(self.username, self.api_token), data=json.dumps(payload))

        if self._last_request.status_code > 200:
            return False

        return json.loads(self._last_request.text)
    

    def _post(self, resource, payload):
        """Make a POST request out to an API uri defined by resource. 
        payload should be a python object that can be json encoded and
        matches what the resource expectes as defined by the API documentation
        """
        self.headers['Content-type'] = "application/json"
        self.headers['Accept'] = "application/json"

        self._last_request = requests.post(self.base_url + resource, headers=self.headers, auth=HTTPBasicAuth(self.username, self.api_token), data=json.dumps(payload))
        
        if self._last_request.status_code > 200:
            return False
        return json.loads(self._last_request.text)





def jobs_summary( api, options={"windowSize" : "1000"} ):    
    """Returns a complete list of tuples containing job number, job id, client name, project, and job name"""
    detail_dict = dict([(d['id'], d) for d in api.jobdetails(options)])
    project_dict = dict([(p['id'], p) for p in api.projects(options)])
    client_dict = dict([(c['id'], c) for c in api.clients(options)])
    ret = []

    for job in api.jobs(options):
        if job['jobDetailId'] in detail_dict.keys():
            detail = detail_dict[job['jobDetailId']]
            if detail['ownerProjectId'] in project_dict.keys():
                project = project_dict[detail['ownerProjectId']]
                if project['clientCRMEntryId'] in client_dict.keys():
                    client = client_dict[project['clientCRMEntryId']]
                    ret.append( (job['jobNumber'], job['id'], client['name'], project['name'], detail['name'] ) )

    return ret






