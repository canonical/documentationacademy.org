#!/usr/bin/env python3

"""Flask Charm entrypoint."""

import logging
import typing

import ops
import paas_charm.flask
from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route

logger = logging.getLogger(__name__)


class OpenDocumentationAcademyCharm(paas_charm.flask.Charm):
    """Flask Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)
        require_nginx_route(
            charm=self,
            service_hostname=self.app.name,
            service_name=self.app.name,
            service_port=self._workload_config.port,
            path_routes="/",
        )

    def _on_ingress_ready(self, *args: typing.Any) -> None:
        return

    def _on_ingress_address_changed(self, *args: typing.Any) -> None:
        return


if __name__ == "__main__":
    ops.main(OpenDocumentationAcademyCharm)
