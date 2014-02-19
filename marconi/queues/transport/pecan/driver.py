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
import collections
from wsgiref import simple_server

from oslo.config import cfg
import pecan
import six

from marconi.openstack.common.gettextutils import _
import marconi.openstack.common.log as logging
from marconi.queues import transport
from marconi.queues.transport import auth, validation
from marconi.queues.transport.pecan.controllers import root

_WSGI_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),

    cfg.IntOpt('port', default=7777,
               help='Port on which the self-hosting server will listen'),

    cfg.IntOpt('content_max_length', default=256 * 1024),
    cfg.IntOpt('metadata_max_length', default=64 * 1024)
]

_WSGI_GROUP = 'drivers:transport:pecan'

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class DriverBase(transport.DriverBase):

    def __init__(self, conf, storage, cache, control):
        super(DriverBase, self).__init__(conf, storage, cache, control)

        self._conf.register_opts(_WSGI_OPTIONS, group=_WSGI_GROUP)
        self._wsgi_conf = self._conf[_WSGI_GROUP]
        self._validate = validation.Validator(self._conf)

        self.app = pecan.Pecan(root.RootController(), hooks=[
            DriverMetadataHook(conf, storage, cache, control)
        ])
        self._init_middleware()

    def _init_middleware(self):
        """Initialize WSGI middlewarez."""
        if self._conf.auth_strategy:
            strategy = auth.strategy(self._conf.auth_strategy)
            self.app = strategy.install(self.app, self._conf)

    def listen(self):
        """Self-host using 'bind' and 'port' from the WSGI config group."""

        msgtmpl = _(u'Serving on host %(bind)s:%(port)s')
        LOG.info(msgtmpl,
                 {'bind': self._wsgi_conf.bind, 'port': self._wsgi_conf.port})

        httpd = simple_server.make_server(self._wsgi_conf.bind,
                                          self._wsgi_conf.port,
                                          self.app)
        httpd.serve_forever()


MarconiDriverConf = collections.namedtuple('MarconiDriverConf', (
    'conf', 'storage', 'cache', 'control'
))


class DriverMetadataHook(pecan.hooks.PecanHook):
    """
    A pecan hook that attaches driver metadata to the request so that it
    can be accessed from within controller code.
    """

    def __init__(self, conf, storage, cache, control):
        self.conf = MarconiDriverConf(conf, storage, cache, control)

    def before(self, state):
        state.request.context['marconi'] = self.conf
