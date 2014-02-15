# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from marconi.queues.transport.pecan.controllers import health as h
from marconi.queues.transport.pecan.controllers import queues as q
from pecan import expose, response


class Controller(object):

    def __init__(self, conf, storage, cache, control):
        self._conf = conf
        self._storage = storage
        self._cache = cache
        self._control = control
        self._health = h.Controller(self._storage)
        self._queues = q.Controller(self._storage)

    @expose()
    def index(self):
        return "welcome to pecan routing"

    @expose()
    def health(self, *remainder):
        print(remainder)
        return self._health.index()


    @expose()
    def queues(self, *remainder):
        print(remainder)
        return self._queues.index()
