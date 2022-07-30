"""
	Databridges Python server Library
	https://www.databridges.io/



	Copyright 2022 Optomate Technologies Private Limited.

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	    http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.
"""

import asyncio

from ..responseHandler import cfrpcResponse
from ..dispatchers import dispatcher
from ..exceptions import dBError
from ..commonUtils import util
from ..remoteProcedure import rpcState
from ..messageTypes import dBTypes

class Crpcserver:
    def __init__(self, servername, sid, dBCoreObject):
        self.__dispatch = dispatcher.dispatcher()
        self.__dbcore = dBCoreObject
        self.__isOnline = False
        self.functions = None
        self.sid = sid
        self.__serverName = servername
        self.__functionNames = ["rpc.response.tracker", "rpc.callee.queue.exceeded",   "dbridges:rpc.server.registration.success",
                                "dbridges:rpc.server.registration.fail", "dbridges:rpc.server.online", "dbridges:rpc.server.offline",
                                "dbridges:rpc.server.unregistration.success", "dbridges:rpc.server.unregistration.fail"]

    def getServerName(self):
        return self.__serverName

    def isOnline(self):
        return self.__isOnline

    def set_isOnline(self, value):
        self.__isOnline = value

    async def register(self):
        try:

            if self.verify_function():
                if asyncio.iscoroutinefunction(self.functions):
                    await self.functions()
                else:
                    self.functions()
        except dBError.dBError as error:
            raise  error

        cStatus = await util.updatedBNewtworkSC(self.__dbcore, dBTypes.messageType.REGISTER_RPC_SERVER,
                                self.__serverName, self.sid, None)
        if not cStatus:
            raise dBError.dBError("E047")


    async def unregister(self):
        cStatus = await util.updatedBNewtworkSC(
            self.__dbcore, dBTypes.messageType.UNREGISTER_RPC_SERVER, self.__serverName, self.sid , None)
        if not cStatus:
            raise dBError.dBError("E047")
        #self.unbind(None,  None)
        #self.functions = None

    def verify_function(self):
        mflag = False
        if self.functions is None:
            raise dBError.dBError("E072")
        if not callable(self.functions):
            raise dBError.dBError("E073")
        mflag = True
        return mflag

    def regfn(self, functionName, callback):
        if not (functionName and not functionName.isspace()):
            raise dBError.dBError("E112")
        if not callback and not callable(callback):
            raise dBError.dBError("E113")

        if functionName in  self.__functionNames:
            raise dBError.dBError("E112")
        if not self.__dispatch.isExists(functionName):
            self.__dispatch.bind(functionName, callback);


    def unregfn(self, functionName, callback):
        if functionName in self.__functionNames:
            return
        self.__dispatch.unbind(functionName, callback);


    def bind(self, eventName, callback):
        if not (eventName and not eventName.isspace()):
            raise dBError.dBError("E074")
        if not callback and not callable(callback):
            raise dBError.dBError("E075")
        if eventName not in self.__functionNames:
            raise dBError.dBError("E074")

        self.__dispatch.bind(eventName, callback)

    def unbind(self, eventName, callback):
        if eventName not in self.__functionNames:
            return
        self.__dispatch.unbind(eventName, callback)

    async def handle_dispatcher(self, functionName, returnSubect, sid, payload):
        response = cfrpcResponse.responseHandler(functionName, returnSubect, sid, self.__dbcore, cfrpcResponse.HandlerTypes.RPC)
        await self.__dispatch.emit_cf(functionName, payload, response)

    async def handle_dispatcher_WithObject(self, functionName, returnSubect, sid, payload, sourceip, sourceid):
        response = cfrpcResponse.responseHandler(functionName, returnSubect, sid, self.__dbcore , cfrpcResponse.HandlerTypes.RPC)

        sessionid = ""
        libtype = ""
        sourceipv4 = ""
        sourceipv6 = ""
        msourceid = ""
        if sourceid:
            strData = str(sourceid).split("#")
            slen = len(strData)
        if slen > 1:
            sessionid = strData[0]
        if slen > 2:
            libtype = strData[1]
        if slen > 3:
            sourceipv4 = strData[2]
        if slen >= 4:
            sourceipv6 = strData[3]

        inOnject = {"inparam": payload, "sessionid": sessionid, "libtype": libtype,
                    "sourceipv4": sourceipv4, "sourceipv6": sourceipv6, "info": sourceip}
        await self.__dispatch.emit_clientfunction(functionName, inOnject, response)

    async def handle_tracker_dispatcher(self, responseid, errorcode):
        await self.__dispatch.emit_cf('rpc.response.tracker', responseid, errorcode)

    async def handle_exceed_dispatcher(self):
        err = dBError.dBError("E070")
        err.updatecode("CALLEE_QUEUE_EXCEEDED")
        await self.__dispatch.emit_cf('rpc.callee.queue.exceeded', err, None)

    async def emit(self, eventName, EventInfo, channelName=None, metadata=None):
        await self.__dispatch.emit(eventName, EventInfo, channelName, metadata)

    async def emit_channel(self, eventName , EventInfo ,  channelName ,  metadata):
        await self.__dispatch.emit_channel(eventName , EventInfo ,  channelName ,  metadata)

    async def emit_channel(self, eventName , EventInfo  ,  metadata):
        await self.__dispatch.emit_channel(eventName , EventInfo  ,  metadata)

    async def resetqueue(self):
        m_status  = await util.updatedBNewtworkCF(self.__dbcore, dBTypes.messageType.RPC_CALLEE_QUEUE_EXCEEDED, None, None, None, None, None, None, None)
        if not m_status:
            raise dBError.dBError("E079")
