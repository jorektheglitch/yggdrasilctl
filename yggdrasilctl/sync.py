import json
from socket import socket
from socket import SOCK_STREAM as tcp, AF_INET as ip

from .utils import preprocess, human_readable
from .errors import APIError


class AdminAPI:

    def __init__(
            self, 
            address:str='localhost', port:int=9001, 
            keepalive:bool=False
    ):
        self.addr = address, port
        self.keepalive = keepalive
        if keepalive:
            self.connection = socket(ip, tcp)
            self.connection.connect(self.addr)

    def _get_connection(self):
        if hasattr(self, 'connection'):
            conn = self.connection
        else:
            conn = socket(ip, tcp)
            conn.connect(self.addr)
        return conn

    def _send_request(self, method:str, **kwargs)->dict:
        req = {'request': method, **kwargs}
        conn = self._get_connection()
        json.dump(req, conn.makefile('w'))
        response = json.load(conn.makefile('r'))
        if not self.keepalive():
            conn.close()
        if not response['status']=='success':
            if 'error' in response:
                response = response['error']
            raise APIError(response)
        return response['response']

    def getSelf(self)->dict:
        """
        Returns exactly one record containing information about the 
        current Yggdrasil node.

        Returns a dict with following keys:
            addr: str - IPv6 address of node
            box_pub_key: str - EncryptionPublicKey of the current node
            build_name: str - build name, if available 
                (e.g. yggdrasil, yggdrasil-develop)
            build_version: str - build version, if available 
                (e.g. 0.3.0, 0.2.7-0091)
            coords: str - coordinates of the node on the spanning tree
            subnet: str - routed IPv6 subnet for this host
        """
        raw = self._send_request('getSelf')
        response = raw['self']
        addr, params = tuple(response.items())[0]
        return dict(addr=addr, **params)

    def getPeers(self)->list:
        """
        Returns one or more records containing information about active peer
        sessions. The first record typically refers to the current node.

        Returns list of dicts which each dict contains keys:
            addr: str - IPv6 address of node
            box_pub_key: str - EncryptionPublicKey of the remote node
            bytes_sent: int - number of bytes sent to that peer
            bytes_recvd: int - number of bytes received from that peer
            endpoint: str - connected IPv4/IPv6 address and port of the peering
            port: int - local switch port number for that peer
            uptime: datetime.timedelta - time since the peer connection was established
        """
        raw = self._send_request('getPeers')
        response = raw['peers']
        return [preprocess(addr=addr, **params) for addr, params in response.items()]

    def getDHT(self)->list:
        """
        Returns known nodes in the DHT.

        Returns list of dicts which each dict contains keys:
            addr: str - IPv6 address of node
            box_pub_key: str - EncryptionPublicKey of the remote node
            coords: str - coordinates of the node on the spanning tree
            last_seen: datetime.datetime - time of last update the DHT record
        """
        raw = self._send_request('getDHT')
        response = raw['dht']
        return [preprocess(addr=addr, **params) for addr, params in response.items()]

    def getSwitchPeers(self)->list:
        """
        Returns zero or more records containing information about switch peers.

        Returns list of dicts which each dict contains keys:
            box_pub_key: str - EncryptionPublicKey of the remote node
            bytes_sent: int - number of bytes sent to the remote node
            bytes_recvd: int - number of bytes received from the remote node
            coords: str - coordinates of the node on the spanning tree
            endpoint: str - connected IPv4/IPv6 address and port of the peering
            ip: str - IPv6 address of the remote node
        """
        raw = self._send_request('getSwitchPeers')
        response = raw['switchpeers']
        return [preprocess(id=_id, **speer) for _id, speer in response.items()]

    def getSessions(self)->list:
        """
        Returns zero or more records containing information about open
        sessions between the current Yggdrasil node and other nodes. 
        Open sessions indicate that traffic has been exchanged with the remote
        node recently.

        Returns list of dicts which each dict contains keys:
            addr: str - IPv6 address of node
            box_pub_key: str - contains the EncryptionPublicKey of the remote node
            bytes_sent: int - contains the number of bytes sent across that session
            bytes_recvd: int - contains the number of bytes received across that session
            coords: str - contains the coordinates of the remote node on the
                spanning tree
            mtu: int - contains the negotiated session MTU between the local end
                and the remote end of the session
            was_mtu_fixed: bool - shows whether or not the MTU has been adjusted 
                since the session was opened to compensate for read errors
        """
        raw = self._send_request('getSessions')
        response = raw['sessions']
        return [preprocess(addr=addr, **params) for addr, params in response.items()]

    def getAllowedEncryptionPublicKeys(self)->list:
        """
        Returns list of strings containing the allowed box public keys.

        If zero strings are returned then it is implied that all connections
        are permitted.
        """
        raw = self._send_request('getAllowedEncryptionPublicKeys')
        return raw['allowed_box_pubs']
