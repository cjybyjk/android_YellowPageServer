from abc import ABC, abstractmethod

class LookupBase(ABC):

    # return a dict contains ('number', 'region', 'type', 'tagstr', 'tag_count') if found number, or return None
    # dict(
    #   number: phone number
    #   region
    #   type:
    #       -1: spam
    #        0: normal
    #        1: service
    #   tagstr: "骚扰", "外卖", "诈骗" etc.
    #   tag_count: Number of users who marked this number
    # )
    @abstractmethod
    def query(self, number):
        pass
    
    @abstractmethod
    def is_supported_region(self, region):
        pass
