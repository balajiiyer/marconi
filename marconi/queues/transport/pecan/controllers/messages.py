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
from marconi.queues.storage import errors as storage_errors
from marconi.queues.transport.wsgi import utils as wsgi_utils
from marconi.queues.transport import utils

LOG = logging.getLogger(__name__)
MESSAGE_POST_SPEC = (('ttl', int), ('body', '*'))

class MessagesController(rest.RestController):

    @property
    def storage(self):
        return request.context['marconi'].storage

    @expose('json')
    def get(self, data):
        pass

    @expose('json')
    def put(self, data):
        pass

    @expose('json')
    def post(self, data):
        print("in post message")
        queue_name = data
        client_uuid = request.headers.get('Client-ID')
        project_id = request.headers.get('x-project-id')

        LOG.debug(_(u'Messages collection POST - queue:  %(queue)s, '
                    u'project: %(project)s'),
                  {'queue': queue_name, 'project': project_id})

        #try:
        #    # Place JSON size restriction before parsing
        #    self._validate.message_length(request.content_length)
        #except Exception as ex:
        #    LOG.exception(ex)
        #    response.status = 400
        #    return "Cannot post message to queue. Validation failed."

        # Pull out just the fields we care about
        messages = wsgi_utils.filter_stream(
            request.stream,
            request.content_length,
            MESSAGE_POST_SPEC,
            doctype=wsgi_utils.JSONArray)

        # Enqueue the messages
        partial = False

        try:
            self._validate.message_posting(messages)

            message_ids = self.storage.message_controller.post(
                queue_name,
                messages=messages,
                project=project_id,
                client_uuid=client_uuid)

        except Exception as ex:
            LOG.exception(ex)
            response.status = 400
            return "Cannot post message to queue. Validation failed."

        except storage_errors.DoesNotExist as ex:
            LOG.debug(ex)
            response.status = 404
            return "Post Message: Queue doesnt exist"

        except storage_errors.MessageConflict as ex:
            LOG.exception(ex)
            partial = True
            message_ids = ex.succeeded_ids

            if not message_ids:
                # TODO(kgriffs): Include error code that is different
                # from the code used in the generic case, below.
                description = _(u'No messages could be enqueued.')
                response.status = 503
                LOG.exception(description)

        except Exception as ex:
            LOG.exception(ex)
            description = _(u'Messages could not be enqueued.')
            response.status = 503
            LOG.exception(description)

        # Prepare the response
        ids_value = ','.join(message_ids)
        response.location = request.path + '?ids=' + ids_value

        hrefs = [request.path + '/' + id for id in message_ids]
        body = {'resources': hrefs, 'partial': partial}
        response.text = utils.to_json(body)
        response.status = 201
