from paasino.arvan_api.api_objects import *
from paasino.log import get_logger
from paasino.constants import (
    const_log,
    const_backend,
    const_kube
)

class App:
    is_secret_successful: bool= None
    is_buildconfig_successful: bool= None
    is_startbuild_successful: bool= None
    is_deployment_successful: bool= None
    is_service_successful: bool= None
    is_route_successful: bool= None
    build_log: str= None
    secret: Secret= None
    buildconfig: BuildConfig=None
    deployment: Deployment=None
    service: Service=None
    route: Route=None
    
    def __init__(self, namespace, name):
        self.name = name
        self.namespace = namespace
        self.logger = get_logger()
        #TODO: namespace creation must be done
    
    
    # TODO: delete create secret and buildconfig and use this instead
    def __create_api_object(self, api_object: APIObject, **kwargs):
        if api_object.get() is not None:
            api_object.delete()
            if api_object.is_deletion_successful:
                return False
            
        api_object.create(**kwargs)
        return api_object.is_creation_successful
    
    
    def __delete_api_object(self, api_object: APIObject):
        if api_object.get() is not None:
                api_object.delete()
                if not api_object.is_deletion_successful:
                    self.__log_error('Garbage Collection', 
                                     api_object.__str__,
                                     'deleting')
        
        
    def __collect_garbage(self):
        if self.buildconfig is not None \
           and self.buildconfig.get_build_status() is not 'Unknown':
            self.buildconfig.delete_build()
            if not self.buildconfig.is_build_deletion_successful: 
                self.__log_error('Garbage Collection', 'build', 'deleting')
                
        api_objects = [
            self.secret,
            self.buildconfig,
            self.deployment,
            self.service,
            self.route
        ]
         # when having network error this may cause some api objects to leak
        for api_object in api_objects:
            if api_object is not None:
                self.__delete_api_object(api_object)
        
       
    def __create_secret(self, git_password: str, git_username: str) -> None:
        if self.secret.get() is not None:
            self.secret.delete()
            if self.secret.is_deletion_successful:
                self.is_secret_successful = False
                return
        self.secret.create(password=git_password, username=git_username)
        self.is_secret_successful = self.secret.is_creation_successful
        #TODO: log the status of secret
        
        
    def __create_buildconfig(self, git_repo_address: str) -> None:
        if self.buildconfig.get() is not None:
            self.buildconfig.delete_buildconfig()
            #TODO: log the existence in namespace as a warning 
            if not self.buildconfig.is_deletion_successful:
                #TODO: log unsuccessful deletion of buildconfig as error
                self.is_buildconfig_successful = False
                return 
        self.buildconfig.create(git_repo_address)
        self.is_buildconfig_successful = self.buildconfig.is_creation_successful
        
        
    def __start_build(self):
        self.buildconfig.build_image()
        self.is_startbuild_successful = self.buildconfig.is_startbuild_successful
        
    
    def __log_error(self, process: str, object_type: str, verb: str):
        self.logger.error(f'There was a problem during {process} of app {self.name} in project {self.namespace} while {verb} {object_type}')
        
        
    def __handle_error(self, process: str, object_type: str, verb: str) -> None:
        self.__log_error(process, object_type, verb)
        self.__collect_garbage()
    
            
    def build_image(self, git_repo_address: str, git_username: str, git_password: str) -> str:
        """
        Builds and image from a git repo
        
        Parameters
        ----------
        git_repo_address: str
            The address of the repo from which source code is pulled
            
        git_username: str
            The username of the owner of the repo
            
        git_password: str
            The password of the repo 
            
        Returns
        ----------
        str:
            The status of the build process 
        """
        self.secret = Secret(self.namespace, self.name)
        self.buildconfig = BuildConfig(self.namespace, self.name)
        
        self.__create_secret(git_password, git_username)
        if not self.is_secret_successful:
            self.__handle_error('build', 'secret', 'creating')
            return const_backend.BUILD_ERROR
        
        self.__create_buildconfig(git_repo_address)
        if not self.is_buildconfig_successful:
            self.__handle_error('build', 'buildconfig', 'creating')
            return const_backend.BUILD_ERROR
        
        self.__start_build()
        if not self.is_startbuild_successful:
            self.__handle_error('build', 'build', 'starting')
            return const_backend.BUILD_ERROR
        
        self.logger.info(f'Successfully started build process of app {self.name} in project {self.namespace}')
        return const_backend.BUILD_STARTED
        
    
    def get_build_status(self):
        if self.is_buildconfig_successful \
           and self.is_secret_successful \
           and self.is_startbuild_successful:
            build_status = self.buildconfig.get_build_status()
            if build_status in const_kube.BuildPhase.UNKNOWN_PHASE:
                return const_backend.UNKNOWN
            if build_status in const_kube.BuildPhase.RUNNING_PHASE:
               return const_backend.BUILD_RUNNING
            elif build_status in const_kube.BuildPhase.COMPLETE_PHASE:
                return const_backend.BUILD_COMPLETE
            else:
                self.__handle_error('build', 'build', 'running')
                return const_backend.BUILD_ERROR
            
            
    def get_build_log(self):
        if self.buildconfig.build.get() is not None:
            return self.buildconfig.get_build_image_logs()
        else: 
            return ''

        
    def deploy_app(self, 
                   image: str,
                   port: int, 
                   cpu: str, 
                   memory: str, 
                   storage: str):
        
        self.deployment = Deployment(self.namespace, self.name)
        self.service = Service(self.namespace, self.name)
        self.route = Route(self.namespace, self.name)
        
        self.is_deployment_successful = self.__create_api_object(
                                            self.deployment, 
                                            image=image,
                                            port=port,
                                            cpu=cpu,
                                            memory=memory,
                                            storage=storage
                                        )
        if not self.is_deployment_successful:
            self.__handle_error('deploy', 'deployment', 'creating')
            return const_backend.DEPLOY_ERROR
        
        self.is_service_successful = self.__create_api_object(
                                        self.service,
                                        port=port
                                    )
        if not self.is_service_successful:
            self.__handle_error('deploy', 'service', 'creating')
            return const_backend.DEPLOY_ERROR
        
        self.is_route_successful = self.__create_api_object(self.route)
        if not self.is_route_successful:
            self.__handle_error('deploy', 'route', 'creating')
            return const_backend.DEPLOY_ERROR
        
        return const_backend.DEPLOY_SUCCESS
    
    
    def delete_app(self):
        api_objects = [
            self.deployment,
            self.service,
            self.route
        ]
         # when having network error this may cause some api objects to leak
        for api_object in api_objects:
            self.__delete_api_object(api_object)
        
        
    def get_app_status(self):
        pass
        
        