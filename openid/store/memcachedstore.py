"""Store using memcached."""

import logging
log = logging.getLogger(__name__)

try:
    import memcache
except ImportError:
    # fall back for Google App Engine -- hasnt been tested though
    from google.appengine.api import memcache

from openid.store import nonce
import time

# mostly ported from https://github.com/openid/ruby-openid/blob/master/lib/openid/store/memcache.rb , but i made some small changes, so there may be bugs. NOT TESTED MUCH




class MemcachedStore(object):
    """In-process memory store.

    Use for single long-running processes.  No persistence supplied.
    """
    def __init__(self, key_prefix= 'openid-store'):
        self.key_prefix = key_prefix

    def _serverKey(self, server_url):
        return self.key_prefix + 'S' + server_url

    def _assocKey(self, server_url, assoc_handle):
        return self.key_prefix + 'A' + server_url + '|' + assoc_handle

    def _nonceKey(self, server_url, timestamp, salt):
        return self.key_prefix + 'N' + str(server_url) + '|' + str(timestamp) + '|' + str(salt)

    def storeAssociation(self, server_url, assoc):
        memcache.set(self._serverKey(server_url), assoc, assoc.lifetime)
        memcache.set(self._assocKey(server_url, assoc.handle), assoc, assoc.lifetime)


    def getAssociation(self, server_url, handle=None):
        if handle is None:
            return memcache.get(self._serverKey(server_url))
        else:
            return memcache.get(self._assocKey(server_url, handle))

    def removeAssociation(self, server_url, handle):
        deleted = memcache.delete(self._assocKey(server_url, handle))
        serverAssoc = memcache.get(self._serverKey(server_url))
        if serverAssoc and serverAssoc.handle == handle:
            deleted = memcache.delete(self._serverKey(server_url)) or deleted
        return deleted
        
    def useNonce(self, server_url, timestamp, salt):
        if abs(timestamp - time.time()) > nonce.SKEW:
            return False

        key = self._nonceKey(server_url, timestamp, salt)

        result = memcache.get(key)
        if (result == None):
            return memcache.set(key, True, nonce.SKEW + 5)
        else:
            return False


    def cleanupNonces(self):
        pass

    def cleanupAssociations(self):
        pass

