#!/usr/bin/env python3

"""Flask Charm entrypoint."""

import logging
import typing

import ops
import paas_charm.flask

logger = logging.getLogger(__name__)


class OpenDocumentationAcademyCharm(paas_charm.flask.Charm):
    """Flask Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)

    def _on_ingress_ready(self, *args: typing.Any) -> None:
        return

    def _on_ingress_address_changed(self, *args: typing.Any) -> None:
        return


if __name__ == "__main__":
    ops.main(OpenDocumentationAcademyCharm)
