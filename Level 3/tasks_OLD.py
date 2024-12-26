import requests
from robocorp import workitems
from robocorp.tasks import task
from RPA.HTTP import HTTP
from RPA.JSON import JSON
from RPA.Tables import Tables

http = HTTP()
json = JSON()
table = Tables()

TRAFFIC_JSON_FILE_PATH = "output/traffic.json"

# JSON data keys
COUNTRY_KEY = "SpatialDim"
YEAR_KEY = "TimeDim"
RATE_KEY = "NumericValue"
GENDER_KEY = "Dim1"

@task
def produce_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Produces traffic data work items.
    """
    http.download(
        url="https://github.com/robocorp/inhuman-insurance-inc/raw/main/RS_198.json",
        target_file=TRAFFIC_JSON_FILE_PATH,
        overwrite=True,
    )
    traffic_data = load_traffic_data_as_table()
    filtered_data = filter_and_sort_traffic_data(traffic_data)
    #assigning list of rows to table variable
    filtered_data = get_latest_data_by_country(filtered_data)
    payloads = create_work_item_payloads(filtered_data)
    save_work_item_payloads(payloads)

@task
def consume_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Consumes traffic data work items.
    """
    for item in workitems.inputs:
        traffic_data = item.payload["traffic_data"]
        if len(traffic_data["country"]) == 3:
            status, return_json = post_traffic_data_to_sales_system(traffic_data)
            if status == 200:
                item.done()
            else:
                item.fail(
                    exception_type="APPLICATION",
                    code="TRAFFIC_DATA_POST_FAILED",
                    message=return_json["message"],
                )
        else:
            item.fail(
                exception_type="BUSINESS",
                code="INVALID_TRAFFIC_DATA",
                message=item.payload,
            )

"""def process_traffic_data():
    for item in workitems.inputs:
        traffic_data = item.payload["traffic_data"]
        valid = validate_traffic_data(traffic_data)

        if valid:
            status = post_traffic_data_to_sales_system(traffic_data)
            if status == 200:
                item.done()
"""
##Doesnt need this function when consumer only called one function. refactoring
def process_traffic_data():
    for item in workitems.inputs:
        traffic_data = item.payload["traffic_data"]
        if len(traffic_data["country"]) == 3:
            status, return_json  = post_traffic_data_to_sales_system(traffic_data)
            if status == 200:
                item.done()
            else:
                item.fail(
                    exception_type= "APPLICATION",
                    code="TRAFFIC_DATA_POST_FAILED",
                    message=return_json
                )
        else:
            item.fail(
                exception_type="BUSINESS",
                code="INVALID_TRAFFIC_DATA",
                message=item.payload,
            )


def validate_traffic_data(traffic_data):
    country = traffic_data["country"]
    """if len(country) == 3:
        return True
    else:
        return False """
    #return boolean value from statement below
    return len(traffic_data["country"]) == 3

def post_traffic_data_to_sales_system(data):
    url = "https://robocorp.com/inhuman-insurance-inc/sales-system-api"
    response = requests.post(url, json=data)
    return response.status_code, response.json()
    #comment raise for status for debuging
    #response.raise_for_status()
    # response.raise for status() return error if send return error.
    """
    This is different but does same ting as :
    #Missing range of successfull 201 202 etc.
    r = requests.get(url)
        if r.status_code == 200:
            # my passing code
        else:
            # anything else, if this even exists

    """
    
def load_traffic_data_as_table():
    json_data = json.load_json_from_file(TRAFFIC_JSON_FILE_PATH)
    return table.create_table(json_data["value"])

def filter_and_sort_traffic_data(data):
    max_rate = 5.0
    both_genders = "BTSX"
    table.filter_table_by_column(data, RATE_KEY, "<", max_rate)
    table.filter_table_by_column(data, GENDER_KEY, "==", both_genders)
    table.sort_table_by_column(data, YEAR_KEY, False)
    return data

def get_latest_data_by_country(data):
    data = table.group_table_by_column(data, COUNTRY_KEY)
    latest_data_by_country = []
    for group in data:
        first_row = table.pop_table_row(group)
        latest_data_by_country.append(first_row)
    # You have list of rows. each index contain a rows.
    return latest_data_by_country

def create_work_item_payloads(traffic_data):
    payloads = []
    for row in traffic_data:
        #dict convert name of variable to name and value to value: country => 'country' and row['Country_key'] => 'SGW
        # this create 'country' : "SGW"
        #This replaces doing manuall structure like = payload = {'country': row[COUNTRY_KEY], 'year'...}
        # OR doing this way: payload['country'] = row[Country_key], just be careful for overriding payload and only appending value not referenses.( can negate it by lowering the scope of variable)
        # You can negate it by also do it by this: mylist.append(mydict.copy())(copy only value not referense) or mydict = {}  # This is a second dictionary refresh and assign new ditionary
        payload = dict(
            country=row[COUNTRY_KEY],
            year=row[YEAR_KEY],
            rate=row[RATE_KEY],
        )
        payloads.append(payload)
    # payloads contains list of dictionary [ {cuntry = row["spatialDim"],year = row["TimeDim"],rate = row["NumericValue"]}]
    
    return payloads

def save_work_item_payloads(payloads):
    for payload in payloads:
        variables = dict(traffic_data=payload)
        workitems.outputs.create(variables)