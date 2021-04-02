import unittest
from paasino.arvan_api import request
from paasino.constants import const_request, const_cluster


class TestGet(unittest.TestCase):
    def test_exception(self):
        req = request.Request("htt//stats.nba.com")
        req.get()
        self.assertEqual(req.status, const_request.UNKNOWN)
        self.assertEqual(req.result, None)
        self.assertEqual(req.message, None)
        self.assertEqual(req.reason, None)
    
    def test_tabular(self):
        # check rows and body and everything
        pass
        
    def test_simple_get(self):
        # simple GET from /healthz
        req = request.Request(f"{const_cluster.BASE_URL}/healthz")
        req.get()
        self.assertEqual(req.status, const_request.OK)
    
    
class TestChange(unittest.TestCase):
    def test_exception(self):
        req = request.Request("htt//stats.nba.com")
        req.change(const_request.DELETE)
        self.assertEqual(req.status, const_request.UNKNOWN)
        self.assertEqual(req.result, None)
        self.assertEqual(req.message, None)
        self.assertEqual(req.reason, None)
        
    def test_correct_post(self):
        pass 
    
    def test_correct_delete(self):
        pass
        
    
if __name__ == '__main__':
    unittest.main()
    
    
    
        
