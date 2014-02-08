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

#from marconi.queues.transport import base
from marconi.queues.transport.pecan.controllers import healthcontroller
from marconi.queues.transport.pecan.controllers import queuescontroller
#from marconi.queues import bootstrap
#from oslo.config import cfg
from pecan import expose


class RootController(object):

    # Ugly, remove this
    qc = None
    mc = None

    #def __init__(self, queue_controller, message_controller):
     #   self.queue_control = queue_controller
      #  self.message_control = message_controller

    def lazy_init(self, queue_controller, message_controller):
        qc = queue_controller
        mc = message_controller

    @expose()
    def index(self):
        return "welcome to pecan routing"

    health = healthcontroller.HealthController()

    # qc and mc are null, because this gets called first, even before
    # when it gets to this point.
    queues = queuescontroller.QueuesController(qc, mc)
