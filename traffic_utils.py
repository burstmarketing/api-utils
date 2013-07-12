from assembla_api import get_space, Assembla_Space
import csv
import time

# Import Job Task Data
def generate_csv_for_import(job_number, space_id, ticket_numbers):
    # api = TrafficAPI(USER_NAME, API_TOKEN)    
    # job_dict = { j['jobNumber'] : j['id'] for j in  api.jobs({"windowSize" : "1000"})}

    field_names = ["jobNumber", 
                   "stageName", 
                   "description", 
                   "note", 
                   "chargeband", 
                   "hours", 
                   "cost", 
                   "total", 
                   "studioHrs", 
                   "hierarchyOrder", 
                   "taskCategory", 
                   "taskUserCategory", 
                   "isComplete", 
                   "startDate", 
                   "deadlineDate" ]

    # Currently just return Administration
    def get_employee_chargeband(id):
        if id is None:
            return "Administration"
        else:            
            # Set up map between employee id's and chargbands
            return "Administration"

    # Add new date formats here as they are encountered in assembla's data
    def normalize_assembla_date_format(d):
        fmt = "%d/%m/%Y"
        try:
            return time.strftime( fmt, time.strptime(d, "%Y-%m-%d"))
        except ValueError:
            try:
                return time.strftime( fmt, time.strptime(d, "%Y/%m/%d"))
            except:
                return ''
                                    

    with open("job_import.csv", "w") as csv_handle:
        csv_file = csv.DictWriter(csv_handle, field_names, restval='')
        csv_file.writeheader()
        
        space = get_space(space_id)
        for ticket in [t for t in space.tickets() if t['number'] in ticket_numbers]:
            # Notes:
            # + should we set this up to pull stageName from the milestone?
            # + Do we need to worry about cost/total or will it figure that out from chareband?
            # + Need to come up with a mapping for employee assembla_id's to chargebands
            # + 
        
            row = { 'jobNumber' : job_number,                    
                    'chargeband' : get_employee_chargeband(t['assigned_to_id']),
                    'description' : ticket['summary'],
                    'note' : ticket['description'],
                    'hours' : ticket['estimate'],
                    'hierarchyOrder' : ticket['number'],
                    'taskCategory' : 'TIME',
                    'isComplete' : 'yes' if ticket['state'] == 0 else 'no',
                    'startDate' : normalize_assembla_date_format(ticket['custom_fields']['Work on Date']),
                    'deadlineDate' : normalize_assembla_date_format(ticket['custom_fields']['Due Date'])
            }
            
            csv_file.writerow({k : v.encode('utf-8') if isinstance(v, basestring) else v for k,v in row.items() })
            

# generate_csv_for_import( "J21", "bHy6wgolir4yZMacwqjQXA", [311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322])






# Currently waiting on response from sonhar ticket:
# http://support.sohnar.com/requests/24660
# 
# def migrate_tickets(job_id, space_id, ticket_numbers):
#     space = get_space(space_id)
#     for ticket in [t for t in space.tickets() if t['number'] in ticket_numbers]:
#         pass
#     return


# "bHy6wgolir4yZMacwqjQXA" - Best Cleaners Space in Assembla
# migrate_tickets(291070, "bHy6wgolir4yZMacwqjQXA", ["320"])

# j = traffic._get("job/291070")
# j['jobTasks'].append({ 
#     "JobId" : 291070,
#     "chargeBandId" : {
#         "Id" : 23956
#         },
#     "description" : "test Test"
# })
# traffic._post("job", j)


