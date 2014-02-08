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

from pecan import expose, rest, response, request
from marconi.openstack.common.gettextutils import _
import marconi.openstack.common.log as logging


LOG = logging.getLogger(__name__)


class QueuesController(rest.RestController):

    __slots__ = ('queue_controller', 'message_controller')

    def __init__(self, queue_controller, message_controller):
        self.queue_controller = queue_controller
        self.message_controller = message_controller

    #Ugly lazy init
    def lazy_init(self, queue_controller, message_controller):
        self.queue_controller = queue_controller
        self.message_controller = message_controller

    @expose('json')
    def index(self):
        response.status = 200
        return "Queues Controller"

    @expose('json')
    def put(self, data):
        project_id = request.headers.get('x-project-id')
        print project_id
        queue_name = data
        created = False
        LOG.debug(_(u'Queue item PUT - queue: %(queue)s, '
                    u'project: %(project)s'),
                  {'queue': queue_name, 'project': project_id})

        try:
            created = self.queue_controller.create(
                queue_name, project=project_id)
            print "queue created"
        except Exception as ex:
            LOG.exception(ex)
            #balajiiyer: wsgi_errors wraps falcon, rewrite this with wsme
            #description = _(u'Queue could not be created.')
            #raise wsgi_errors.HTTPServiceUnavailable(description)

        response.status = 201 if created else 204
        response.location = request.path
        response.status = 201
