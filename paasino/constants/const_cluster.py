import os 

BASE_URL = 'https://napi.arvancloud.com/paas/v1/regions/ir-thr-at1/o'

API_KEY = os.getenv('AR_API_KEY')

HEADERS = {
    "content-type": "application/json",
    "Authorization": f"Bearer Apikey {API_KEY}",
    "Accept": "application/json, */*",
    "User-Agent": "oc/v1.11.0+d4cacc0 (linux/amd64) kubernetes/d4cacc0"   
}

GET_HEADERS = {
    "content-type": "application/json",
    "Authorization": f"Bearer Apikey {API_KEY}",
    "Accept": "application/json;as=Table;v=v1beta1;g=meta.k8s.io, application/json",
    "User-Agent": "oc/v1.11.0+d4cacc0 (linux/amd64) kubernetes/d4cacc0"
}

DOCKER_REGISTRY_SECRET = 'private-reg' 
DOCKER_REGISTRY_ADDRESS = os.getenv('AR_REGISTRY')

NAMESPACE = os.getenv('AR_NAMESPACE')
DOMAIN_NAME_BASE = f'{NAMESPACE}.apps.ir-thr-at1.arvan.run'