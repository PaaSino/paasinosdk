from paasino.arvan_api import api_objects
from paasino.constants import const_cluster

username='' # FILL ME
password='' # FILL ME
address='' # FILL ME

secret = api_objects.Secret(namespace=const_cluster.NAMESPACE, name='private-reg')
secret.create(password=password,
              username=username,
              server=address,
              secret_type='docker')
secret.get()
