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

import abc
import functools
import itertools
from wsgiref import simple_server

import falcon
from oslo.config import cfg
import six

from marconi.common import decorators
from marconi.common.transport import version
from marconi.common.transport.wsgi import helpers
from marconi.common import utils
from marconi.openstack.common.gettextutils import _
import marconi.openstack.common.log as logging
from marconi.queues import transport
from marconi.queues.transport import auth
from marconi.queues.transport import validation

_WSGI_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),

    cfg.IntOpt('port', default=8888,
               help='Port on which the self-hosting server will listen'),
]

_WSGI_GROUP = 'drivers:transport:wsgi'

LOG = logging.getLogger(__name__)


def _config_options():
    return itertools.chain(utils.options_iter(_WSGI_OPTIONS, _WSGI_GROUP))


@six.add_metaclass(abc.ABCMeta)
class DriverBase(transport.DriverBase):

    def __init__(self, conf, storage, cache, control):
        super(DriverBase, self).__init__(conf, storage, cache, control)

        self._conf.register_opts(_WSGI_OPTIONS, group=_WSGI_GROUP)
        self._wsgi_conf = self._conf[_WSGI_GROUP]
        self._validate = validation.Validator(self._conf)

        self.app = None
        self._init_routes()
        self._init_middleware()

    @decorators.lazy_property(write=False)
    def before_hooks(self):
        """Exposed to facilitate unit testing."""
        return [
            helpers.require_accepts_json,
            helpers.extract_project_id,

            # NOTE(kgriffs): Depends on project_id being extracted, above
            functools.partial(helpers.validate_queue_identification,
                              self._validate.queue_identification)
        ]

    def _init_routes(self):
        """Initialize hooks and URI routes to resources."""
        self.app = falcon.API(before=self.before_hooks)
        version_path = version.path()
        for route, resource in self.bridge:
            self.app.add_route(version_path + route, resource)

    def _init_middleware(self):
        """Initialize WSGI middlewarez."""

        # NOTE(flaper87): Install Auth
        if self._conf.auth_strategy:
            strategy = auth.strategy(self._conf.auth_strategy)
            self.app = strategy.install(self.app, self._conf)

    @abc.abstractproperty
    def bridge(self):
        """Constructs a list of route/responder pairs that can be used to
        establish the functionality of this driver.

        Note: the routes should be unversioned.

        :rtype: [(str, falcon-compatible responser)]
        """
        raise NotImplementedError

    def listen(self):
        """Self-host using 'bind' and 'port' from the WSGI config group."""

        msgtmpl = _(u'Serving on host %(bind)s:%(port)s')
        LOG.info(msgtmpl,
                 {'bind': self._wsgi_conf.bind, 'port': self._wsgi_conf.port})

        httpd = simple_server.make_server(self._wsgi_conf.bind,
                                          self._wsgi_conf.port,
                                          self.app)
        httpd.serve_forever()
