
from requests import Session

class Flowdock:
    """Simple wrapper for Flowdock REST API."""

    API_URL = "https://api.flowdock.com"

    def __init__(self, api_key, debug=False, print_function=None):
        """Initialize Flowdock API wrapper.

        @param debug Print debug info if True
        @param print_function Use this function to print debug info. By default
        use python builtin print. Mainly for using click.echo without requiring
        click as dependency.
        """
        self.session = Session()
        # requests accepts http basic auth as tuple (user, pass), however,
        # Flowdoc uses only api key as username without password
        self.session.auth = (api_key, None)
        self.debug = debug
        self.print = print_function if print_function else print

    def get_organizations(self):
        """Get list of organizations this user has access to"""
        url = "{}/organizations".format(self.API_URL)
        if self.debug:
            self.print("Sending GET request to URL {}".format(url))
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def find_user_orgs(self, email):
        """Find organizations this user belongs to"""
        orgs = self.get_organizations()
        return [org for org in orgs if Flowdock.user_in_org(email, org)]

    @staticmethod
    def user_in_org(email, org):
        """Chek if user is part of organization"""
        for user in org['users']:
            if user['email'] == email:
                return True
        return False

    def delete_user_from_org(self, user, org):
        url = "{}/organizations/{}/users/{}".format(self.API_URL,
                                                    org['parameterized_name'],
                                                    user['id'])
        if self.debug:
            self.print("Sending DELETE request to url {}".format(url))

        r = self.session.delete(url)
        r.raise_for_status()

    def close(self):
        self.session.close()
