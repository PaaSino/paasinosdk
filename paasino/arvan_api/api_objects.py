from paasino.constants import const_cluster, const_kube, const_request
from paasino.arvan_api.request import Request
from paasino.log import get_logger
from base64 import b64encode
import json
import os 


#TODO: put the name of the objects and functions in the logs
class APIObject:
    selflink: str= ''
    name: str= ''
    namespace: str= ''
    base_url: str= ''
    is_creation_successful: bool = False
    is_deletion_successful: bool = False
    creation_manifest: dict= {}
    deletion_manifest: dict= None
    creation_manifest_path: str= '' 

    def __init__(self, namespace: str, name: str):
        self.name = name
        if namespace is not None:
            self.namespace = namespace
        self._set_selflink()
        self.__set_base_url()
        self.__set_creation_manifest_path()
        self.req = Request(self.base_url)
        self.logger = get_logger()
        
    def _log_http_request_problem(self):
        self.logger.error(f'{self.req.result}')
        self.logger.error(f'Message -> {self.req.message} Reason -> {self.req.reason}')
        
    def _read_creation_manifest(self):
        with open(self.creation_manifest_path) as creation_file:
            self.creation_manifest = json.load(creation_file)
            
    def __set_creation_manifest_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.creation_manifest_path = f'{dir_path}/json/apply-{self.__str__()}.json'
        
    def __set_base_url(self):
        self.base_url = f'{const_cluster.BASE_URL}/{self.selflink}'
        
    def _set_selflink(self):
        self.selflink =  f'{self._api_group()}/namespaces/{self.namespace}/{self.__str__()}' 
    
    def _api_group(self) -> str:
        return ''
    
    def _check_http_ok(self):
        return self.req.status == const_request.OK
    
    def _create_pod_label(self):
        pod_label = const_kube.DEPLOYMENT_LABEL
        pod_label[const_kube.DEPLOYMENT_LABEL_KEY] = self.name
        return pod_label
    
    def _fill_creation_manifest(self, **kwargs):
        pass
        
    def create(self,  **kwargs):
        self._read_creation_manifest()
        self._fill_creation_manifest(**kwargs)
        self.req.change(const_request.POST, headers=const_cluster.HEADERS,
                        body=self.creation_manifest)
        if self.req.is_successful:    
                self.is_creation_successful = True
        else: 
            self._log_http_request_problem()

    def delete(self):
        endpoint = f'/{self.name}'
        self.req.change(const_request.DELETE, endpoint=endpoint, headers=const_cluster.HEADERS,
                        body=self.deletion_manifest)
        
        if self.req.is_successful:
            self.is_deletion_successful = True
        else:
            self._log_http_request_problem()
            
    def get(self):
        endpoint = f'/{self.name}'
        self.req.get(endpoint=endpoint, headers=const_cluster.HEADERS, is_json=True)
        if self.req.is_successful:    
                return self.req.result_json
        else: 
            self._log_http_request_problem()
            return None
    
    

class Deployment(APIObject):
    deletion_manifest = {
        "propagationPolicy": "Background"
    }
    
    def __init__(self, namespace: str, name: str):
        super().__init__(namespace, name)
        self.pod = Pod(namespace, name)
    
    def __str__(self):
        return 'deployments'
    
    def _api_group(self) -> str:
        return 'apis/apps/v1'
    
    def __create_container_resources(self, cpu, memory, storage):
        res = const_kube.RESOURCE_TEMPLATE
        resources = {
            'cpu': cpu,
            'memory': memory,
            'ephemeral-storage': storage
        }
        res['limits'] = resources
        res['requests'] = resources
        return res
        
    def _fill_creation_manifest(self, 
                                image: str, 
                                port: str, 
                                cpu: str, 
                                memory: str, 
                                storage: str):
        
        self.creation_manifest['metadata']['name'] = self.name
        pod_label = self._create_pod_label() 
        self.creation_manifest['spec']['selector']['matchLabels'] = pod_label
        self.creation_manifest['spec']['template']['metadata']['labels']= pod_label
        self.creation_manifest['spec']['template']['spec']['containers'][0]['image'] = image
        self.creation_manifest['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort'] = \
            port
        self.creation_manifest['spec']['template']['spec']['containers'][0]['resources'] = \
            self.__create_container_resources(cpu, memory, storage)
    
    # def create(self, image: str, port: int, cpu :str, memory: str, storage: str) -> None:
    #     """
    #     Creates a deployment 
    #     """
    #     #TODO: complete docs for functions
    #     self._read_creation_manifest()
    #     self._fill_creation_manifest(image, port, cpu, memory, storage)
    #     self.req.change(const_request.POST, headers=const_cluster.HEADERS,
    #                     body=self.creation_manifest)

    #     if self.req.is_successful:    
    #         self.is_creation_successful = True
    #     else: 
    #         self._log_http_request_problem()
        
    def get_pod_status(self) -> str:
        pod_info = self.pod.get_with_label()
        self.logger.info(f'{pod_info}')
        if len(pod_info) == 0:
            return const_kube.UNKNOWN
        return pod_info[0].get('status', const_kube.UNKNOWN)
    
    def get_pod_log(self) -> str:
        return self.pod.get_log()
    
    
class Pod(APIObject):
    def __init__(self, namespace, name):
        super().__init__(namespace, name)
        
    def __str__(self):
        return 'pods'
    
    def _api_group(self) -> str:
        return 'api/v1'
    
    def __parse_container_info(self, rows: list) -> list:
        if len(rows) == 0:
            return []
        containers_info_all = []
        for row in rows:
            if len(row[const_kube.CELLS]) < 5:
                #TODO: log this row
                continue
            container_info = {}
            container_info['name'] = row[const_kube.CELLS][0]
            container_info['status'] = row[const_kube.CELLS][2]
            container_info['restarts'] = row[const_kube.CELLS][3]
            container_info['age'] = row[const_kube.CELLS][4]
            containers_info_all.append(container_info)
        return containers_info_all
        
    def get_with_label(self) -> list:
        """
        Gets list of pods in a deployment using a label selector
        """
        label = {
            'labelSelector': f'{const_kube.DEPLOYMENT_LABEL_KEY}={self.name}'
        }
        self.req.get(params=label, headers=const_cluster.GET_HEADERS, is_tabular=True)
        if self._check_http_ok():
            #TODO: log success 
            rows = self.req.rows
            return self.__parse_container_info(rows)
        self.logger.error(f'Got an error when retrieving pod with label in deployment {self.name}')
        return []
    
    def get_log(self, pod_name: str=None) -> str:
        if pod_name is None:
            pod_info = self.get_with_label()
            if len(pod_info) == 0:
                self.logger.warning(f'Zero length pod_info for delpoyment {self.name}')
                return ''
            
            pod_name = pod_info[0].get('name', None)
            if pod_name is None:
                self.logger.warning(f'No "name" for pod in deployment {self.name}')
                return ''
        
        endpoint = f'/{pod_name}/log'
        self.req.get(endpoint=endpoint, headers=const_cluster.HEADERS)
        if self.req.status == const_request.OK:
            self.logger.info(self.req.result)
            #TODO: properly log the status as info
            return self.req.result
        self.logger.error(f'Got an error when getting logs for pod with name {pod_name}')
        self._log_http_request_problem()
        return ''
    
    
class BuildConfig(APIObject):
    deletion_manifest = {
        "propagationPolicy": "Background"
    }
    #TODO: add build phases 
    build_manifest: dict= None
    is_startbuild_successful: bool= None
    is_build_deletion_successful: bool=None
    
    
    def __init__(self, namespace, name):
        super().__init__(namespace, name)
        self.__set_buildconfig_manifest_path()
        self.build = Build(namespace, name)
        
    def __set_buildconfig_manifest_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.buildconfig_manifest_path = f'{dir_path}/json/start-{self.__str__()}.json'
        
    def _api_group(self) -> str:
        return 'apis/build.openshift.io/v1'
    
    def __str__(self):
        return 'buildconfigs'
    
    def __create_image_name(self):
        return f'{self.name}:latest'
    
    def _fill_creation_manifest(self, git_repo_address: str) -> None:
        self.creation_manifest['metadata']['name'] = self.name
        self.creation_manifest['spec']['output']['pushSecret']['name'] = \
            const_cluster.DOCKER_REGISTRY_SECRET
        self.creation_manifest['spec']['output']['to']['name'] = \
            const_cluster.DOCKER_REGISTRY_ADDRESS + self.__create_image_name()
        self.creation_manifest['spec']['source']['git']['uri'] = git_repo_address
        self.creation_manifest['spec']['source']['sourceSecret']['name'] = self.name
    
    def create(self, git_repo_address: str) -> None:
        self._read_creation_manifest()
        self._fill_creation_manifest(git_repo_address)
        self.req.change(const_request.POST, headers=const_cluster.HEADERS,
                        body=self.creation_manifest)
        #TODO: is_successful and const_request.OK are the same thing
        if self.req.is_successful:    
                self.is_creation_successful = True
        else: 
            self._log_http_request_problem()
        
    # def check_buildconfig_exists(self) -> bool:
    #     endpoint = f'/{self.name}'
    #     self.req.get(endpoint=endpoint, headers=const_cluster.HEADERS, is_json=True)
    #     if self._check_http_ok():    
    #         #TODO: check based on different ranges of status code
    #         return True
    #     else:
    #         self._log_http_request_problem()
    #         return False
    
    def delete_buildconfig(self):
        super().delete()
        
    def __read_build_manifest(self):
        with open(self.buildconfig_manifest_path) as build_file:
            self.buildconfig_manifest = json.load(build_file)
            
    def __fill_build_manifest(self):
        self.buildconfig_manifest['metadata']['name'] = self.name
        
    def build_image(self):
        endpoint = f'/{self.name}/instantiate'
        self.__read_build_manifest()
        self.__fill_build_manifest()
        self.req.change(method=const_request.POST, endpoint=endpoint, headers=const_cluster.HEADERS,
            body=self.buildconfig_manifest)
        
        if self.req.is_successful:    
                self.is_startbuild_successful = True
                self.logger.info(self.req.result)
        else: 
            self._log_http_request_problem()
    
    def get_build_status(self) -> str:
        return self.build.get_status()
    
    def get_build_image_logs(self):
        return self.build.get_logs()
    
    def delete_build(self):
        self.build.delete()
        self.is_build_deletion_successful = self.build.is_deletion_successful
    
    
class Build(APIObject):
    def __init__(self, namespace, name):
        super().__init__(namespace, name)
        self.name = f'{name}-1'
        self.pod = Pod(namespace, self.name)
        
    def _api_group(self) -> str:
        return 'apis/build.openshift.io/v1'
    
    def __str__(self):
        return 'builds'
    
    def __extract_phase(self):
        status = self.req.result_json.get('status', None)
        if status is None:
            return const_kube.UNKNOWN 
        return status.get('phase')
    
    def get_status(self) -> str:
        endpoint = f'/{self.name}'
        self.req.get(endpoint=endpoint, headers=const_cluster.HEADERS, is_json=True)
        if self._check_http_ok():  
            self.logger.info(self.req.result_json)  
            return self.__extract_phase()
        else:
            self._log_http_request_problem()
            return const_kube.UNKNOWN
        
    def get_logs(self):
        return self.pod.get_log(f'{self.name}-build')
    

class Service(APIObject):
    def __init__(self, namespace, name):
        super().__init__(namespace, name)
        
    def _api_group(self) -> str:
        return 'api/v1'
    
    def __str__(self):
        return 'services'
    
    def _fill_creation_manifest(self, port: int):
        self.creation_manifest['metadata']['name'] = self.name 
        self.creation_manifest['spec']['ports'][0]['name'] = f'{self.name}-port' 
        self.creation_manifest['spec']['ports'][0]['targetPort'] = port
        self.creation_manifest['spec']['selector'] = self._create_pod_label()
     
    
        

class Secret(APIObject):
    def __init__(self, namespace, name):
        super().__init__(namespace, name)
    
    def _api_group(self) -> str:
        return 'api/v1'
    
    def __str__(self):
        return 'secrets'
    
    def __create_docker_config(self, password: str, username: str, server: str):
        auth = b64encode(bytes(f"{username}:{password}", 'ascii')).decode('ascii')
        
        docker_config = {
            "auths":{
                server:{
                    "username": username,
                    "password": password,
                    "auth": auth
                }
            }
        }
        
        # replace single quote with double quote and return bytes
        docker_config = str(docker_config)
        docker_config = docker_config.replace('\'', '\"')
        return b64encode(bytes(docker_config, 'ascii')).decode('ascii')
        
   
    def _fill_creation_manifest(self, password: str, username: str,
                                secret_type: str='Opaque', server: str=None):
        self.creation_manifest['metadata']['name'] = self.name
        if secret_type == 'Opaque':
            self.creation_manifest['stringData'] = {}
            self.creation_manifest['stringData']['password'] = password
            self.creation_manifest['stringData']['username'] = username
            self.creation_manifest['type'] = secret_type
        else:
            self.creation_manifest['data'] = {}
            self.creation_manifest['data']['.dockerconfigjson'] = \
                self.__create_docker_config(password, username, server)
            self.creation_manifest['type'] = 'kubernetes.io/dockerconfigjson'
        
        
class Route(APIObject):
    def __init__(self, namespace, name):
        super().__init__(namespace, name)
        
    def _api_group(self) -> str:
        return 'apis/route.openshift.io/v1'
    
    def __str__(self):
        return 'routes'
    
    def _fill_creation_manifest(self):
        self.creation_manifest['metadata']['name'] = self.name
        self.creation_manifest['spec']['host'] = f'{self.name}-{const_cluster.DOMAIN_NAME_BASE}'
        self.creation_manifest['spec']['port']['targetPort'] = f'{self.name}-port'
        self.creation_manifest['spec']['to']['name'] = self.name
        

class Project(APIObject):
    'apis/project.openshift.io/v1/projectrequests'
    def __init__(self, name):
        super().__init__(None, name)
        
    def __set_base_url(self):
        self.base_url = f'{const_cluster.BASE_URL}/{self.selflink}'
        
    def _set_selflink(self):
        self.selflink =  f'{self._api_group()}/{self.__str__()}' 
        
    def _api_group(self) -> str:
        return 'apis/project.openshift.io/v1'
    
    def __str__(self):
        return 'projectrequests'
    
    def _fill_creation_manifest(self):
        self.creation_manifest['metadata']['name'] = self.name
     
    #TODO: handle get of it    
    # def get(self):
    #     request = Request()
    #     endpoint = f'/{self.name}'
    #     self.req.get(endpoint=endpoint, headers=const_cluster.HEADERS, is_json=True)
    #     if self.req.is_successful:    
    #             return self.req.result_json
    #     else: 
    #         self._log_http_request_problem()
    #         return None