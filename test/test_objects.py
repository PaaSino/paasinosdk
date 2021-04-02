import random
import string
import unittest
import time
from paasino.arvan_api.api_objects import (
    APIObject,
    Deployment,
    BuildConfig,
    Service,
    Secret,
    Route,
    Project
)
from paasino.constants import const_request, const_kube

NAMESPACE = 'amirmahdi'

class TestObject(unittest.TestCase):
    def get_random_string(self):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(8))
        return result_str
    
    def check_object_health(self, api_object: APIObject):
        self.assertEqual(api_object.req.is_successful, True)
        self.assertEqual(api_object.req.message, None)
        self.assertEqual(api_object.req.reason, None)
        self.assertEqual(api_object.is_creation_successful, True)
        

class TestDeployment(TestObject):
    def test_create_get_delete_deployment(self):
        #TODO: seperate get and create
        #TODO: check the correctnesss using curl command
        deployment = Deployment('amirmahdi', 'proj-'+self.get_random_string())
        deployment.create(image='nginx', port=80, cpu='1', memory='1G', storage='3G')
        self.check_object_health(deployment)
        time.sleep(15)
        self.assertEqual(deployment.get_pod_status(), const_kube.RUNNING)
        deployment.delete()
        self.assertEqual(deployment.is_deletion_successful, True)
        time.sleep(15)
        self.assertEqual(deployment.get_pod_status(), const_kube.UNKNOWN)
        
    def test_deployment_pod_log(self):
        deployment = Deployment('amirmahdi', 'log-'+self.get_random_string())
        deployment.create(image='nginx', port=80, cpu='1', memory='1G', storage='3G')
        self.check_object_health(deployment)
        time.sleep(15)
        self.assertIsNotNone(deployment.get_pod_log())
        deployment.delete()
        time.sleep(15)
        self.assertEqual(deployment.get_pod_status(), const_kube.UNKNOWN)
        
    def test_quota_limit_exceed(self):
        pass
        #TODO: create multiple delpoyments to exceed quotas and check reaction
        
class TestBuild(TestObject):
    def test_create_get_buildconfig(self):
        name = 'build-' + self.get_random_string()
        buildconfig = BuildConfig(NAMESPACE, name)
        buildconfig.create(git_secret_name='secret', 
            git_repo_address='http://gitlab.com/nodejs.git')
        self.check_object_health(buildconfig)
        self.assertIsNotNone(buildconfig.get())
        buildconfig.delete_buildconfig()
        self.assertEqual(buildconfig.is_deletion_successful, True)
        self.assertIsNone(buildconfig.get())
        
    def test_build_image_wrong_repo(self):
        name = 'build-' + self.get_random_string()
        buildconfig = BuildConfig(NAMESPACE, name)
        buildconfig.create(git_secret_name='secret', 
            git_repo_address='http://gitlab.com/nodejs.git')
        self.check_object_health(buildconfig)
        self.assertIsNotNone(buildconfig.get())
        buildconfig.build_image()
        self.assertTrue(buildconfig.is_startbuild_successful)
        time.sleep(15)
        self.assertEqual(buildconfig.get_build_status(), 'Failed')
        # delete build
        buildconfig.delete_build()
        self.assertEqual(buildconfig.get_build_status(), 'Unknown')
        self.assertTrue(buildconfig.is_build_deletion_successful)
        buildconfig.delete_buildconfig()
        self.assertTrue(buildconfig.is_deletion_successful)
        self.assertIsNone(buildconfig.get())
        
    #TODO: add tests for correct builds
    
    
class TestService(TestObject):
    def test_create_delete_service(self):
       name = 'service-' + self.get_random_string() 
       service = Service(NAMESPACE, name)
       service.create(port=80)
       self.check_object_health(service)
       self.assertIsNotNone(service.get())
       service.delete()
       self.assertTrue(service.is_deletion_successful)
       self.assertIsNone(service.get())
       
class TestSecret(TestObject):
    def test_create_delete_opaque_secret(self):
        name = 'secret-' + self.get_random_string()
        secret = Secret(NAMESPACE, name)
        secret.create(username='leo', password='mano')
        self.check_object_health(secret)
        self.assertIsNotNone(secret.get())
        secret.delete()
        self.assertTrue(secret.is_deletion_successful)
        self.assertIsNone(secret.get())
    
    def test_create_delete_docker_secret(self):
        name = 'secret-' + self.get_random_string()
        secret = Secret(NAMESPACE, name)
        secret.create(username='leo', password='mano',
                      secret_type='docker', server='my.server')
        self.check_object_health(secret)
        self.assertIsNotNone(secret.get())
        secret.delete()
        self.assertTrue(secret.is_deletion_successful)
        self.assertIsNone(secret.get())
        
    
        
#TODO: these last 3 objects are exactly the same  
class TestRoute(TestObject):
    def test_create_delete_route(self):
        name = 'route-' + self.get_random_string()
        route = Route(NAMESPACE, name)
        route.create(username='leo', password='mano')
        self.check_object_health(route)
        self.assertIsNotNone(route.get())
        route.delete()
        self.assertTrue(route.is_deletion_successful)
        self.assertIsNone(route.get())
        
class TestProject(TestObject):
    def test_create_delete_project(self):
        name = 'project-' + self.get_random_string()
        project = Project(name)
        project.create()
        self.check_object_health(project)
        self.assertIsNotNone(project.get())
        project.delete()
        self.assertTrue(project.is_deletion_successful)
        self.assertIsNone(project.get())
   
        
if __name__ == '__main__':
    unittest.main()