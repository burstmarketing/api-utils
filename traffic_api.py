from requests.auth import HTTPBasicAuth
import requests
import json

class TrafficAPI():
    def __init__(self, username, api_token):
        self.username = username
        self.api_token = api_token

        self.base_url = "https://production-sohnar.apigee.com/TrafficLiteServer/openapi/"
        self.headers = {"Accept" : "application/json"}
        self.max_attempts = 10
        self._last_request = None
        self._last_response = None

    def _get(self,resource, options={}):
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
        self._last_response = self._get("crm/client", options)
        return self._last_response['resultList']


    def projects(self,options={}):
        self._last_response = self._get("project", options)
        return self._last_response['resultList']

    def jobs(self,options={}):
        self._last_response = self._get("job", options)
        return self._last_response['resultList']

    def jobdetails(self,options={}):
        self._last_response = self._get("jobdetail", options)
        return self._last_response['resultList']


    def _put(self, resource, payload):
        self.headers['Content-type'] = "application/json"
        self.headers['Accept'] = "application/json"

        self._last_request = requests.put(self.base_url + resource, headers=self.headers, auth=HTTPBasicAuth(self.username, self.api_token), data=json.dumps(payload))

        if self._last_request.status_code > 200:
            return False

        return json.loads(self._last_request.text)
    

    def _post(self, resource, payload):
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






