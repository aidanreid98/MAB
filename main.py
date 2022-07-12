
from pyiseers import ERS
import json



#connect to the CISCO ISE API
def connectAPI(username, password):
    ise = ERS(ise_node='10.20.125.237', ers_user=username, ers_pass=password, verify=False, disable_warnings=True, timeout=10)
    return ise

#structure the endpoint group response from ISE API into python dictionaries
def toDict(group):
    newDict={}
    newDict["Group Name"]=group[0]
    newDict["Group ID"]=group[1]
    newDict["Group Description"]=group[2]
    return newDict

#get all endpoint groups containing EPIC
def getEndpointGroups(ise,  filterTerm = "EPIC"):
    APIresponse = ise.get_endpoint_groups(size=100)
    groupList=[]
    for i in APIresponse['response']:
        if i[0][0:4] == filterTerm:
            iDict=toDict(i)
            groupList.append(iDict)

    return APIresponse['success'], groupList

#get all MAC addressess associated with a certain group NOTE: This only returns the first 100 groups
def getGroupMACs(ise,id):
    APIresponse = ise.get_endpoints(groupID=id, size=100)

    if APIresponse['response']:
        macList=APIresponse['response']
    else:
        macList="No MAC Addresses found to be associated with given Group ID."

    return APIresponse['success'], macList

#input validation to make sure that the mac provided is valid
def validateMAC(ise, mac):
    flag=ise._mac_test(mac)
    if not flag:
        raise Exception("Invalid MAC Address")

#validation to ensure that the connection to the ISE API is functional
def validateISEConnection(ise):
    APIResponse = ise.get_endpoint_groups(size=100)
    if not APIResponse['success']:
        if APIResponse['response'] =="Unauthorized":
            raise Exception("Login failed. Check username and password.")
        else:
            raise Exception(APIResponse['response'])


#identify the group associated with a given MAC address
def getEndpointGroup(ise,mac):

    APIresponse = ise.get_endpoint(mac)
    return APIresponse['success'], APIresponse['response']

#add an endpoint to a group
def addEndpoint(ise, mac, name, group_id, description):

    APIresponse = ise.add_endpoint(name=name, mac=mac, group_id=group_id, description=description)
    return APIresponse['success'], APIresponse['response']

#delete an endpoint
def deleteEndpoint(ise, mac):

    APIresponse = ise.delete_endpoint(mac)
    return APIresponse['success'], APIresponse['response']



def main():

    #define default values for the variables to be returned in json
    success = "False"
    error = ""
    response = ""

    try:


        #connect to the API and validate the connection
        ise = connectAPI("epic_ers", "8Aqq[cWb") #(@option.username@, @option.password@)
        validateISEConnection(ise)

        #defines which operation will be done
        #operation=@option.operation@
        operation = "listGroupMACs"


        if operation == "add": #add an endpoint to a group

            mac="97:F8:81:95:7D:F8"    #@option.mac@
            validateMAC(ise, mac)
            name="endpoint-test9"   #@option.name@
            group_id="734f2d70-6731-11ec-8316-d6257cefda7a"   #@option.group_id@
            description="endpoint-test9"   #@option.description@

            success, response = addEndpoint(ise, mac, name, group_id, description)

        elif operation == "remove": #remove an endpoint from ise
            mac="97:F8:81:95:7D:F8"    #@option.mac@
            validateMAC(ise, mac)
            success, response = deleteEndpoint(ise, mac)

        elif operation == "listGroupMACs": #list all the MAC addresses associated with a group
            group_id="734f2d70-6731-11ec-8316-d6257cefda7b"   #@option.group_id@
            success, response = getGroupMACs(ise, group_id)

        elif operation == "listGroups": #list all endpoint groups and their IDs associated with EPIC
            success, response = getEndpointGroups(ise, filterTerm="EPIC")

        elif operation == "listMACGroups": #list endpoint groups associated with a certain MAC Address
            mac="00:44:02:03:04:05"    #@option.mac@
            validateMAC(ise, mac)
            success, response = getEndpointGroup(ise, mac)

    #catch any errors and store them to be output
    except Exception as e:
        error = str(e)

    #format the output
    outputDict = {}
    outputDict['success'] = success
    outputDict['response'] = response
    outputDict['error'] = error
    print(outputDict)
    print(json.dumps(outputDict))


if __name__ == "__main__":
    main()


