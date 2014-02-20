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

    @property
    def storage(self):
        return request.context['marconi'].storage

    # Haven't found a native way to do this in pecan.
    @staticmethod
    def _query_to_kwargs(name, value, store=None):

        if store is not None:
            if value is not None:
                store[name] = value

    @expose('json')
    def get_all(self, detailed=None, marker=None, limit=None):

        kwargs = {}
        project_id = request.headers.get('x-project-id')

        self._query_to_kwargs('detailed', detailed, kwargs)
        self._query_to_kwargs('marker', marker, kwargs)
        #handle exception for the cast here
        self._query_to_kwargs('limit', int(limit), kwargs)

        print(len(kwargs))

        results = self.storage.queue_controller.list(
            project=project_id,
            **kwargs
        )

        # Buffer list of queues
        queues = list(next(results))

        # Check for an empty list
        if len(queues) == 0:
            print("Len is 0")
            response.status = 204
            return

         # Got some. Prepare the response.
        kwargs['marker'] = next(results)
        for each_queue in queues:
            each_queue['href'] = request.path + each_queue['name']

        response_body = {
            'queues': queues,
            'links': [
                {
                    'rel': 'next',
                    'href': request.path
                }
            ]
        }

        return response_body

    @expose('json')
    def put(self, data):
        project_id = request.headers.get('x-project-id')
        print(project_id)
        queue_name = data
        LOG.debug(_(u'Queue item PUT - queue: %(queue)s, '
                    u'project: %(project)s'),
                  {'queue': queue_name, 'project': project_id})

        try:
            created = self.storage.queue_controller.create(
                queue_name, project=project_id)
        except Exception as ex:
            # TODO(balajiiyer): rewrite this with wsme
            LOG.exception(ex)
            response.status = 503
            return "Could not create queue"

        response.status = 201 if created else 204
        response.location = request.path

    @expose('json')
    def delete(self, data):

        queue_name = data
        project_id = request.headers.get('x-project-id')

        LOG.debug(_(u'Queue item DELETE - queue: %(queue)s, '
                    u'project: %(project)s'),
                  {'queue': queue_name, 'project': project_id})
        try:
            self.storage.queue_controller.delete(
                queue_name, project=project_id
            )

        except Exception as ex:
            LOG.exception(ex)

        response.status = 204

    @expose('json')
    def head(self, data):

        queue_name = data
        project_id = request.headers.get('x-project-id')

        LOG.debug(_(u'Queue item exists - queue: %(queue)s, '
                    u'project: %(project)s'),
                  {'queue': queue_name, 'project': project_id})

        if self.storage.queue_controller.exists(
                queue_name, project=project_id
        ):
            response.status = 204
        else:
            response.status = 404

        response.content_location = request.path
