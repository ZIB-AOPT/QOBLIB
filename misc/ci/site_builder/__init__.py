# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""QOBLIB static-site data builder.

A small package that scans the QOBLIB repository and emits the JSON data
consumed by the static frontend in ``website/``. It deliberately produces only
data — never HTML. See :mod:`site_builder.build` for the entry points and
:mod:`site_builder.config` for the build context and static metadata.
"""

from __future__ import annotations

from . import config
from .build import build_data, build_site, copy_static_frontend

__all__ = ["config", "build_site", "build_data", "copy_static_frontend"]
