import json
from socket import socket, error as socket_error
from socket import SOCK_STREAM as tcp, AF_INET as ip

from datetime import datetime as dt, timedelta as td
from typing import List, Dict, Any, Union

from .utils import preprocess, human_readable
from .errors import APIError, APIUnreachable


class AdminAPI:
    """
    Class wrapper for Yggrasil admin API's methods.
    """
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

    def _get_connection(self)->socket:
        if hasattr(self, 'connection'):
            conn = self.connection
        else:
            conn = socket(ip, tcp)
            try:
                conn.connect(self.addr)
            except socket_error:
                raise APIUnreachable("Can't connect to {}:{}".format(*self.addr))
        return conn

    def _send_request(self, method:str, **kwargs)->dict:
        req = {'request': method, **kwargs}
        conn = self._get_connection()
        try:
            json.dump(req, conn.makefile('w'))
            response = json.load(conn.makefile('r'))
        finally:
            if not self.keepalive:
                conn.close()
        if not response['status']=='success':
            if 'error' in response:
                response = response['error']
            raise APIError(response)
        return response['response']

    def getSelf(self)->Dict[str, str]:
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

    def getPeers(self)->List[Dict[str, Union[str, int, td]]]:
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

    def getSwitchPeers(self)->List[Dict[str, Union[str, int]]]:
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
    
    def addPeer(self, uri:str) -> Dict[str, List[str]]:
        """
        Adds a new peer.
        
        Params:
            uri: str - peer to added, in standard URI format as used in the
                configuration file, i.e. tcp://a.b.c.d:e

        Returns a dict with following keys:
            added: list - peers sucessfully added
            not_added: list - peers failed to add
        """
        return self._send_request('addPeer', uri=uri)

    def removePeer(self, port) -> Dict[str, List[str]]:
        """
        Removes an existing peer.
        
        Params:
            port: int - port of the peer to remove, this can be looked up using
                getPeers or getSwitchPorts

        Returns a dict with following keys:
            removes: list - peers sucessfully removed
            not_removed: list - peers failed to remove
        """
        return self._send_request('removePeer', port=port)

    def getSessions(self)->List[Dict[str, Union[str, int, bool]]]:
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

    def getAllowedEncryptionPublicKeys(self)->List[str]:
        """
        Returns list of strings containing the allowed box public keys.

        If zero strings are returned then it is implied that all connections
        are permitted.
        """
        raw = self._send_request('getAllowedEncryptionPublicKeys')
        return raw['allowed_box_pubs']

    def addAllowedEncryptionPublicKey(
        self, box_pub_key:str
    ) -> Dict[str, List[str]]:
        """
        Adds a new allowed box pub key.
        
        Params:
            box_pub_key: str - public key to add
        
        Returns a dict with following keys:
            added: list - box pub keys sucessfully added
            not_added: list - box pub keys failed to add
        """
        return self._send_request(
            'addAllowedEncryptionPublicKey', box_pub_key=box_pub_key
        )

    def removeAllowedEncryptionPublicKey(
        self, box_pub_key:str
    ) -> Dict[str, List[str]]:
        """
        Removes an existing box pub key.
        
        Params:
            box_pub_key: str - public key to remove
        
        Returns a dict with following keys:
            removes: list - box pub keys sucessfully removed
            not_removed: list - box pub keys failed to remove
        """
        return self._send_request(
            'removeAllowedEncryptionPublicKey', box_pub_key=box_pub_key
        )

    def getDHT(self)->List[Dict[str, Union[str, dt]]]:
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

    def DHTping(
        self, box_pub_key:str=None, coords:str=None, target:str=None
    ) -> List[Dict[str, str]]:
        """
        Asks a remote node to respond with information from the DHT.

        Params:
            addr: str - IPv6 address of node
            box_pub_key: str - x25519 public key of target node (hex hormat)
            coords: str - coordinates of target node (in network tree)

        Returns list of dicts which each dict contains keys:
            box_pub_key: str - contains the EncryptionPublicKey of the remote node
            coords: str - contains the coordinates of the node on the spanning tree
        """
        if target:
            nodes = self._send_request(
                'DHTping', box_pub_key=box_pub_key, coords=coords, target=target
            )
        else:
            nodes = self._send_request(
                'DHTping', box_pub_key=box_pub_key, coords=coords
            )
        return [{'addr': addr, **stats} for addr, stats in nodes['nodes'].items()]
    
    def getNodeInfo(self, box_pub_key:str=None, coords:str=None)->Any:
        """
        Asked a remote node for it's NodeInfo.
        
        Params:
            box_pub_key: str - x25519 public key of target node (hex hormat)
            coords: str - coordinates of target node (in network tree)
        """
        raw = self._send_request(
            'getNodeInfo', box_pub_key=box_pub_key, coords=coords
        )
        return raw['nodeinfo']

    def getTunTap(self)->Dict[str, Union[str, int, bool]]:
        """
        Returns exactly one record containing information about the current
        node’s TUN/TAP adapter.

        Returns a dict with following keys:
            name: str - name of Yggdrasil interface
            tap_mode: bool - shows whether or not the interface is in TAP mode 
                (if false then TUN mode is implied)
            mtu: int - contains the MTU of the local TUN/TAP adapter
        """
        raw = self._send_request('getTunTap')
        name, props = raw.items()
        props[0].update({'name': name[0]})
        return props[0]

    def getMulticastInterfaces(self)->List[str]:
        """
        Returns list of strings containing the enabled multicast peering interfaces.

        If zero strings are returned then it is implied that multicast peering
        is not allowed on any interface.
        """
        raw = self._send_request('getMulticastInterfaces')
        return raw['multicast_interfaces']

    def getRoutes(self)->Dict[str, str]: 
        """
        Returns zero or more records where the subnet (string) is mapped to
        the public key (string).
        """
        raw = self._send_request('getRoutes')
        return raw['routes']

    def addRoute(
        self, subnet:str, box_pub_key:str
    ) -> Dict[str, List[str]]:
        """
        Adds a new crypto-key route.

        Params:
            subnet: str - subnet that will routed
            box_pub_key: str - public key of node that will route to

        Returns a dict with following keys:
            added: list - routes that sucessfully added
            not_added: list - routes that failed to add
        """
        return self._send_request(
            'addRoute', subnet=subnet, box_pub_key=box_pub_key
        )

    def removeRoute(
        self, subnet:str, box_pub_key:str
    ) -> Dict[str, List[str]]:
        """
        Removes an existing crypto-key route.

        Params:
            subnet: str - routed subnet
            box_pub_key: str - public key of node that routed to

        Returns a dict with following keys:
            removed: list - routes that sucessfully removed
            not_removed: list - routes that failed to remove
        """
        return self._send_request(
            'removeRoute', subnet=subnet, box_pub_key=box_pub_key
        )

    def getSourceSubnets(self)->List[str]:
        """
        Returns list of allowed crypto-key routing source subnets.
        """
        raw = self._send_request('getSourceSubnets')
        return raw['source_subnets']

    def addSourceSubnet(self, subnet:str) -> Dict[str, List[str]]:
        """
        Adds a new crypto-key source subnet.

        Params:
            subnet: str - subnet to allow traffic from

        Returns a dict with following keys:
            added: list - subnets that sucessfully added
            not_added: list - subnets that failed to add
        """
        return self._send_request('addSourceSubnet', subnet=subnet)

    def removeSourceSubnet(self, subnet:str) -> Dict[str, List[str]]:
        """
        Removes an existing crypto-key source subnet.

        Params:
            subnet: str - subnet from which traffic is allowed

        Returns a dict with following keys:
            removed: list - subnets that sucessfully removed
            not_removed: list - subnets that failed to remove
        """
        return self._send_request('removeSourceSubnet', subnet=subnet)
