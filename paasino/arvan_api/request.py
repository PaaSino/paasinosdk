import requests
from paasino.constants import const_request, const_kube, const_log
from paasino.log import get_logger


class Request(object):
    base_url: str= ""
    response: dict= None
    status_code: int= -1
    message: str= None
    reason: str= None
    result: str= None    
    result_json: dict=None
    rows :list=[]
    is_successful :bool = None 
    CHANGE_METHODS = {
        const_request.POST: requests.post,
        const_request.DELETE: requests.delete 
    }
    
    
    def __init__(self, base_url :str):
        self.base_url = base_url
        self.logger = get_logger()
            
            
    def get(self, endpoint: str="", params: dict=None , headers: dict=None,
            body: dict=None, is_tabular: bool=False, is_json: bool=False) -> None:
        """
        Performs a customized http GET request
        """
        
        url = self.base_url + endpoint
        self.__send_request(url, requests.get, headers=headers, json=body, params=params)
        
        self.__handle_response()
        
        if self.status == const_request.OK:
            if is_tabular:
                response_json = self.response.json()
                self.rows = response_json['rows']
            if is_json:
                self.result_json = self.response.json()
            
    
    def change(self, method :str, endpoint :str="", params :dict=None , headers :dict=None,
            body :dict=None) -> None:
        """
        Performs a customized http POST or DELETE request
        """
        
        url = self.base_url + endpoint
        self.__send_request(url, self.CHANGE_METHODS[method], headers=headers, json=body, params=params)
        
        self.__handle_response()
            
                    
    def __send_request(self, url :str, method, **kwargs):
        try:
            self.response = method(url, **kwargs) 
            self.status_code = self.response.status_code
            self.result = self.response.text
            #TODO: log status code and response and body
        except Exception as e:
            #TODO: use logging 
            #TODO: log status code and response and body
            self.response = None
            self.status_code = -1
            print(e)
            
    
    def __handle_response(self) -> None:
        if self.status == const_request.OK:
            self.is_successful = True
        else:
            self.is_successful = False
            if self.response is None:
                return 
            try:
                response_json = self.response.json()
            except Exception as e:
                self.logger.error(e)
                return
                
            if response_json == None:
                self.message = None
                self.reason = None
                return
            kind = response_json.get(const_kube.KIND, '')
        
            if kind == const_kube.STATUS_VALUE:
                self.message = response_json.get(const_kube.MESSAGE, '')
                self.reason = response_json.get(const_kube.REASON, '')


    @property    
    def status(self) -> str:
        if self.status_code in range(200, 300):
            return const_request.OK
        elif self.status_code in range(300, 600):
            return const_request.NOT_OK
        else:
            return const_request.UNKNOWN
        