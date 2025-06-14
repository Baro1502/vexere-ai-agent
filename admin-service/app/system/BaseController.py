from flask import Blueprint
from app.system import Res

class BaseController(Blueprint, Res):
    def create(self):
        pass
    
    def get(self):
        return self.res('get method',200) 
    
    def get_all(self):
        return self.res('get_all method',200) 
    
    def delete(self):
        return self.res('delete method',200)