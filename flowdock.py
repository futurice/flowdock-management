"""Simple module for using parts of Flowdock REST API"""
from __future__ import print_function
from datetime import datetime, timedelta
from requests import Session


class Flowdock(object):
    """Simple wrapper for Flowdock REST API."""

    API_URL = "https://api.flowdock.com"

    def __init__(self, api_key, debug=False, print_function=None):
        """Initialize Flowdock API wrapper.

        debug -- Print debug info if True
        print_function -- Use this function to print debug info. By default use
        python builtin print. Mainly for using click.echo without requiring
        click as dependency.
        """
        self.session = Session()
        # requests accepts http basic auth as tuple (user, pass), however,
        # Flowdoc uses only api key as username without password
        self.session.auth = (api_key, None)
        self.print_debug = debug
        self.print = print_function if print_function else print

    def debug(self, message):
        if self.print_debug:
            self.print(message)

    def list_organizations(self):
        """List the organizations this user has access to"""
        url = "{}/organizations".format(self.API_URL)
        self.debug("Sending GET request to URL {}".format(url))
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def find_user_orgs(self, email):
        """Find organizations given user belongs to"""
        orgs = self.list_organizations()
        return [org for org in orgs if Flowdock.user_in_org(email, org)]

    @staticmethod
    def user_in_org(email, org):
        """Chek if user is part of organization"""
        for user in org['users']:
            if user['email'].lower() == email.lower():
                return True
        return False

    def delete_user_from_org(self, user, org):
        """Delete given user from given organization."""
        url = "{}/organizations/{}/users/{}".format(
            self.API_URL, org['parameterized_name'], user['id'])
        self.debug("Sending DELETE request to url {}".format(url))

        res = self.session.delete(url)
        res.raise_for_status()

    def find_inactive_in_org(self, org, days=90, null=False):
        """Find inactive users in Flowdock organization

        Flowdock has unofficial API /organizations/:organization/audits/users/
        that list when users have been last active in that organization. It is
        undocumented but seems to work fairly well. This method lists users
        that have not been active during last days.

        Arguments:
        org -- parameterized flowdock organization name to check
        Keyword arguments:
        days -- how many days since last activity is considered inactive.
        null -- list users whose last activity date is not known for some
        reason.
        """
        url = "{}/organizations/{}/audits/users/".format(
            self.API_URL, org)
        self.debug("Sending GET request to URL {}".format(url))
        res = self.session.get(url)
        res.raise_for_status()
        users = res.json()

        if null:
            return [x for x in users if x['accessed_at'] is None]

        limit = datetime.now() - timedelta(days=days)
        users = [x for x in users if x['accessed_at'] is not None]
        users = [x for x in users if _last_access_before(x, limit)]
        return users

    def close(self):
        """Close the http session used internally.

        This method should be called when the API object is not needed anymore
        to free resources from client and server.
        """
        self.session.close()


def _last_access_before(user, limit):
    """Was the last access time of the user object before given datetime"""
    last = datetime.strptime(user['accessed_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    return last < limit
