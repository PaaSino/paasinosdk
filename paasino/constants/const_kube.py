# kubernetes key 
KIND = 'kind'
STATUS_KEY = 'status'
REASON = 'reason'
MESSAGE = 'message'

# kubernetes values
STATUS_VALUE = 'Status'
FAILURE = 'Failure'

# kubernetes subobjects
RESOURCE_TEMPLATE = {
    "requests":{
        "cpu":"1",
        "ephemeral-storage":"2G",
        "memory":"1G"
    },
    "limits":{
        "cpu":"1",
        "ephemeral-storage":"2G",
        "memory":"1G"
    },
}

DEPLOYMENT_LABEL_KEY = 'customer'
DEPLOYMENT_LABEL = {
    DEPLOYMENT_LABEL_KEY:"customer1"
}

# kubernetes pod status
RUNNING = 'Running'
PENDING = 'Pending'
SUCCEEDED = 'Succeeded'
FAILED = 'Failed'
UNKNOWN = 'Unknown'

INITIALIZING = 'initializing'
CELLS = 'cells'

# kubernetes objects
BUILDCONFIG = 'BuildConfig'

#openshift build phase
class BuildPhase():
    RUNNING_PHASE: list= [
        'New',
        'Pending',
        'Running'
    ]
    
    COMPLETE_PHASE: list= [
        'Complete'
    ]
    
    ERROR_PHASE: list= [
        'Failed',
        'Error',
        'Cancelled'
    ]
    
    UNKNOWN_PHASE: list= [
        UNKNOWN
    ]