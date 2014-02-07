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

from marconi.queues.transport import base
from marconi.queues.transport.pecan.controllers import healthcontroller
#from marconi.queues.transport.pecan.controllers import queuescontroller
from pecan import expose
import marconi.common.cache
import marconi.queues.

class RootController(object):



    @expose()
    def index(self):
        return "weclome to pecan routing"

    health = healthcontroller.HealthController()
    #queues = queuescontroller.QueuesController()
