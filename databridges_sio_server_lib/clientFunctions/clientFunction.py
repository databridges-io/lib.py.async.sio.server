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

from ..commonUtils import aioPromise, util, aioTimer
from ..dispatchers import dispatcher
from ..exceptions import dBError
from ..messageTypes import dBTypes
from ..responseHandler import cfrpcResponse
from ..events import dBEvents
import json
import random


class cfclient:
    def __init__(self, dBCoreObject):
        self.__dispatch = dispatcher.dispatcher();
        self.__dbcore = dBCoreObject;
        self.enable = False;
        self.functions = None;
        self.__sid_functionname={}
        self.__callerTYPE = "cf"
        self.__functionNames = ['cf.response.tracker', 'cf.callee.queue.exceeded']

    def verify_function(self):
        mflag = False;
        if self.enable:
            if self.functions is None:
                raise dBError.dBError("E009")
            if not callable(self.functions):
                raise dBError.dBError("E010")
            mflag = True;
        else:
            mflag = True;
        return mflag;


    def regfn(self, functionName, callback):
        if not (functionName and not functionName.isspace()):
            raise dBError.dBError("E110")
        if not callback and not callable(callback):
            raise dBError.dBError("E111")
        if functionName in  self.__functionNames:
            raise dBError.dBError("E110")

        self.__dispatch.bind(functionName, callback);


    def unregfn(self, functionName, callback):
        if functionName in self.__functionNames:
            return
        self.__dispatch.unbind(functionName, callback);


    def bind(self, eventName, callback):
        if not (eventName and not eventName.isspace()):
            raise dBError.dBError("E066")
        if not callback and not callable(callback):
            raise dBError.dBError("E067")

        if eventName not in self.__functionNames:
            raise dBError.dBError("E066")
        self.__dispatch.bind(eventName, callback);

    def unbind(self, eventName, callback):
        if eventName not in self.__functionNames:
            return
        self.__dispatch.unbind(eventName, callback);

    def unbind(self, eventName):
        if eventName not in self.__functionNames:
            return
        self.__dispatch.unbind(eventName, None)

    async def handle_dispatcher(self, functionName, returnSubect, sid, payload):
        try:
            response = cfrpcResponse.responseHandler(functionName, returnSubect, sid, self.__dbcore, cfrpcResponse.HandlerTypes.CF)
            await self.__dispatch.emit_cf(functionName, payload, response);
        except Exception as e:
            k=1

    async def handle_tracker_dispatcher(self, responseid, errorcode):
        await self.__dispatch.emit_cf('cf.response.tracker', responseid, errorcode);

    async def handle_exceed_dispatcher(self):
        err = dBError.dBError("E070")
        err.updateCode("CALLEE_QUEUE_EXCEEDED");
        await self.__dispatch.emit_cf('cf.callee.queue.exceeded', err, None);

    async def handle_callResponse(self, sid, payload, isend, rsub):
        if sid in self.__sid_functionname:
            metadate = {"functionName": self.__sid_functionname[sid]};
            await self.__dispatch.emit_clientfunction2(sid, payload, isend,rsub)

    def GetUniqueSid(self, sid):
        nsid = sid + util.GenerateUniqueId();
        if nsid in self.__sid_functionname:
            nsid = ("" + str(random.randint(0, 999999)))
        return nsid

    async def __call_internal(self, sessionid , functionName ,  inparameter, sid, progress_callback):
        async def internal_call(resolve,reject):
            interal_result = False
            cstatus = None;
            if self.__callerTYPE== 'rpc':
                cstatus = await util.updatedBNewtworkCF(self.__dbcore, dBTypes.messageType.CALL_RPC_FUNCTION, sessionid, functionName , None , sid ,  inparameter );
            else:
                cstatus = await util.updatedBNewtworkCF(self.__dbcore , dBTypes.messageType.CF_CALL, sessionid, functionName , None,  sid ,  inparameter, None, None );

            if not cstatus:
                if self.__callerTYPE == 'rpc':
                    reject( dBError.dBError("E079"))
                else:
                    reject(dBError.dBError("E068"))

            async def internal_response(response , rspend, rsub):
                nonlocal interal_result
                dberror = None
                if not rspend:
                    if progress_callback and callable(progress_callback):
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(response);
                        else:
                            progress_callback(response);
                else:
                    if rsub is not None:
                        ursub =  str(rsub).upper()
                        if ursub == "EXP":
                            eobject = json.loads(response)
                            if self.__callerTYPE == 'rpc':
                                dberror = dBError.dBError("E055")
                                dberror.updateCode(eobject["c"], eobject["m"] )
                                reject(dberror)
                                interal_result = True
                            else:
                                dberror = dBError.dBError("E071");
                                dberror.updateCode(eobject["c"], eobject["m"] );
                                reject(dberror)
                                interal_result = True
                        else:
                            if self.__callerTYPE == 'rpc':
                                dberror = dBError.dBError("E054")
                                dberror.updateCode(ursub, "" )
                                reject(dberror)
                                interal_result = True
                            else:
                                dberror = dBError.dBError("E070")
                                dberror.updateCode(ursub , "")
                                reject(dberror)
                                interal_result = True
                    else:
                        resolve(response)
                        interal_result = True
                    self.__dispatch.unbind(sid , None)
                    del self.__sid_functionname[sid]
            self.__dispatch.bind(sid ,  internal_response)
            while not interal_result:
                await asyncio.sleep(1)

        p = aioPromise.Promise()
        await p.Execute(internal_call)
        return p



    async def call(self, sessionid, functionName ,  inparameter ,  ttlms , progress_callback):
        loop_index = 0
        loop_counter = 3
        mflag = False
        sid_created = True

        sid = util.GenerateUniqueId()
        while loop_index < loop_counter and not mflag:
            if sid in self.__sid_functionname:
                sid = self.GetUniqueSid(sid)
                loop_index = loop_index + 1
            else:
                self.__sid_functionname[sid] = functionName
                mflag = True

        if not mflag:
            sid = ("" + str(random.randint(0, 999999)))
            if not sid in self.__sid_functionname:
                self.__sid_functionname[sid] = functionName
            else:
                sid_created = False

        if not sid_created:
            raise dBError.dBError("E107")
            return

        async def _call(resolve , reject):
            async def timeexpire():
                self.__dispatch.unbind(sid)
                del self.__sid_functionname[sid]
                reject(dBError.dBError("E069"))
                await util.updatedBNewtworkCF(
                    self.__dbcore , dBTypes.messageType.RPC_CALL_TIMEOUT, None,sid,None , None , None , None , None );
            if ttlms < 100:
                new_ttlms = ttlms / 1000
            else:
                new_ttlms = ttlms
            r = aioTimer.Timer(new_ttlms, timeexpire)

            def successResolve(value):
                r.cancel()
                resolve(value)
            def successReject(value):
                r.cancel()
                reject(value)

            p = await self.__call_internal(sessionid ,functionName , inparameter,sid ,  progress_callback)
            p.then(successResolve).catch(successReject)
            return p

        pr = aioPromise.Promise()
        await pr.Execute(_call)
        return pr

    async def resetqueue(self):
        m_status  = await util.updatedBNewtworkCF(self.__dbcore, dBTypes.messageType.CF_CALLEE_QUEUE_EXCEEDED, None, None, None, None, None, None, None)
        if not m_status:
            raise dBError.dBError("E068")