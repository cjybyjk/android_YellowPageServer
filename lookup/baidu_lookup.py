from .lookup_base import LookupBase

class BaiduLookup(LookupBase):
    def query(self, number):
        return None

    def is_supported_region(self, region):
        return False
