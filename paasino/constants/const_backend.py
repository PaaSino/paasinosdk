"""
A bunch of constants for transferring the state to backend
"""

# different status for backend procedures
# build:
BUILD_ERROR = 'BuildError'
BUILD_STARTED = 'BuildStarted'
BUILD_RUNNING = 'BuildRunning'
BUILD_COMPLETE = 'BuildComplete'
UNKNOWN = 'Unknown'

# status for deploying app
DEPLOY_ERROR = 'DeployError'
DEPLOY_SUCCESS = 'DeploySuccess'