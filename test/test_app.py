import random
import string
import unittest
import time
from paasino.backend.app import App
from paasino.constants import const_backend

NAMESPACE = 'amirmahdi'

class TestApp(unittest.TestCase):
    def get_random_string(self):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(8))
        return result_str
    
    def build_image(self, repo_address, username, password):
        name = 'app-' + self.get_random_string()
        app = App(NAMESPACE, name)
        build_status = app.build_image(repo_address, username, password)
        self.assertEqual(build_status, const_backend.BUILD_STARTED)
        build_status = app.get_build_status()
        self.assertEqual(build_status, const_backend.BUILD_RUNNING)
        time.sleep(20)
        build_log = app.get_build_log()
        self.assertIsNotNone(build_log)
        build_status = app.get_build_status()
        self.assertIsNotNone(build_status)
        print(build_status)
        
    def test_build_image_wrong(self):
        repo_address = 'https://github.com/jamzi/coreapi.git'
        username = ''
        password = ''
        self.build_image(repo_address, username, password)
        
    def test_build_image(self):
        repo_address = 'https://github.com/srcmaxim/nodeapp.git'
        username = ''
        password = ''
        self.build_image(repo_address, username, password)
        
    def deploy_app(self, image, port, cpu, memory, storage):
        name = 'app-' + self.get_random_string()
        app = App(NAMESPACE, name)
        deploy_status = app.deploy_app(image, port, cpu, memory, storage)
        time.sleep(20)
        self.assertEqual(deploy_status, const_backend.DEPLOY_SUCCESS)
        # TODO: request to nginx 
        app.delete_app()
        
        
    def test_deploy_nginx(self):
        self.deploy_app('nginx', 80, '800m', '1G', '1G')
        
        # the route: f'{self.name}-{const_cluster.DOMAIN_NAME_BASE}'
        
        
    def test_deploy_built_image(self):
        pass
        
        
if __name__ == '__main__':
    unittest.main()