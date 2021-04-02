from paasino.deploy import app
from paasino.constants import const_cluster, const_backend
import time, os

NAMESPACE = 'amirmahdi' # FILL ME
NAME = 'leo444nino1021' # FILL ME, THE UNIQUE APP NAME

GIT_REPO_ADDRESS = 'https://github.com/aliakbar-hemmati/docker-tutorial' # FILL ME
GIT_PASSWORD = '' # FILL ME, IF REQUIRED
GIT_USERNAME = '' # FILL ME, IF REQUIRED 

IMAGE_NAME = const_cluster.DOCKER_REGISTRY_ADDRESS + f'{NAME}:latest'

django_app = app.App(NAMESPACE, NAME)

print('**********************************')
print('************ BUILD ***************')
print('**********************************')
print('******** Starting build  *********')
django_app.build_image(GIT_REPO_ADDRESS, GIT_USERNAME, GIT_PASSWORD)

print('******** Checking build  *********')
status = const_backend.UNKNOWN
while status != const_backend.BUILD_COMPLETE:
    time.sleep(20)
    print(django_app.get_build_log())
    status = django_app.get_build_status()
    print(status)
    if status == const_backend.BUILD_ERROR:
        exit(1)

print('**********************************')
print('************ DEPLOY **************')
print('**********************************')
print('********* Deploying app **********')
django_app.deploy_app(IMAGE_NAME, 8000, '200m', '1G', '1G')

print(f"Check this link to see your app: {NAME}-{NAMESPACE}.apps.ir-thr-at1.arvan.run")