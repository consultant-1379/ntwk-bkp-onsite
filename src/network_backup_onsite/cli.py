##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

# For the (syntax-error)
# pylint: disable=E0001

"""Module allowing for ``python -m ntwk_bkp_onsite <arguments>``."""

import main as application


def main():
    """Execute the main bit of the application."""
    application.main()
