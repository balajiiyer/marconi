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

"""Marconi Storage Drivers"""

from marconi.queues.storage import base
from marconi.queues.storage import errors  # NOQA

# Hoist classes into package namespace
ControlDriverBase = base.ControlDriverBase
DataDriverBase = base.DataDriverBase
CatalogueBase = base.CatalogueBase
Claim = base.Claim
Message = base.Message
Queue = base.Queue
ShardsBase = base.ShardsBase

DEFAULT_QUEUES_PER_PAGE = base.DEFAULT_QUEUES_PER_PAGE
DEFAULT_MESSAGES_PER_PAGE = base.DEFAULT_MESSAGES_PER_PAGE
DEFAULT_SHARDS_PER_PAGE = base.DEFAULT_SHARDS_PER_PAGE

DEFAULT_MESSAGES_PER_CLAIM = base.DEFAULT_MESSAGES_PER_CLAIM
