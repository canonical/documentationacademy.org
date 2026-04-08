# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for the documentationacademy.org charm."""

import pathlib
import sys

CHARM_DIR = pathlib.Path(__file__).parents[2]
sys.path.insert(0, str(CHARM_DIR / "lib"))
sys.path.insert(0, str(CHARM_DIR / "src"))

import paas_charm.flask  # noqa: E402
from ops import testing  # noqa: E402

import charm  # noqa: E402


class TestCharm:
    """Test charm basics."""

    def test_charm_is_flask_charm(self):
        """CharmCharm is a paas_charm Flask charm."""
        assert issubclass(charm.CharmCharm, paas_charm.flask.Charm)

    def test_charm_starts(self):
        """Charm can be instantiated."""
        ctx = testing.Context(charm.CharmCharm)
        container = testing.Container("flask-app", can_connect=True)
        state = testing.State(containers={container}, leader=True)

        ctx.run(ctx.on.start(), state)
