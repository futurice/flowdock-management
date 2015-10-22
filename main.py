#!/usr/bin/env python
import sys
import click
from flowdock import Flowdock


# This is the common endpoint for all commands. Handle common options here
@click.group()
@click.option('--debug', default=False, is_flag=True,
              help='Turn on debug ouptut')
@click.option('--api_key', help='Flowdock API key for the user')
@click.pass_obj
def cli(obj, api_key, debug):
    """Simple command line utility for managing Flowdock users.

    The script needs a personal Flowdock API KEY to function. Get one from
    https://flowdock.com/account/tokens and give it to this script either as
    option --api_key or as environment variable FLOWDOCK_API_KEY

    To get more help for subcommands run "flowdock COMMAND --help", for example
    "flowdock find_users --help"
    """
    obj['APIKEY'] = api_key
    obj['DEBUG'] = debug

    if not api_key:
        click.echo("NO FLOWDOCK API KEY PROVIDED!")
        sys.exit(1)

    if debug:
        click.echo("Got api key: {}".format(obj['APIKEY']))


@cli.command(short_help="List Flowdock organizations")
@click.pass_obj
def list_orgs(obj):
    """List flowdock organizations this user is part of."""
    click.echo("Getting organization list...")
    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    orgs = f.list_organizations()
    f.close()
    for org in orgs:
        print_org(org)


@cli.command(short_help="Find user from organisations")
@click.argument('email')
@click.pass_obj
def find_user(obj, email):
    """List the organizations the given user belongs to

    This only lists the organizations both you and the given user are part of.
    """
    click.echo("Listing the organizations {} belongs to".format(email))
    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    user_orgs = f.find_user_orgs(email)
    f.close()
    if len(user_orgs) == 0:
        click.echo("User not found!")
    click.echo("User is part of the following Flowdock organizations:")
    for org in user_orgs:
        click.echo(org['name'])


@cli.command(short_help="Delete user")
@click.argument('email')
@click.pass_obj
def delete_user(obj, email,):
    """Delete user with given EMAIL address from all Flowdock organizations.

    The user is deleted only from organizations that you are admin of.
    """
    click.echo("Deleting user {} from all organizations...".format(email))
    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    orgs = f.find_user_orgs(email)
    if len(orgs) == 0:
        click.echo("User not found!")
        return
    click.echo("User is part of the following Flowdock organizations:")
    for org in orgs:
        click.echo(org['name'])
    if click.confirm('Are you sure you want to delete user?'):
        _delete_user_from_orgs(f, email, orgs)
        click.echo('Done!')
    f.close()


def _delete_user_from_orgs(flowdock, email, orgs):
    # Get the user object related to the email address
    user = None
    for org_user in orgs[0]['users']:
        if org_user['email'] == email:
            user = org_user
    for org in orgs:
        flowdock.delete_user_from_org(user, org)


@cli.command(short_help="List inactive users")
@click.option('--null', default=False, is_flag=True,
              help="List users whose last login is unknown")
@click.option('--days', default=90,
              help='How many days since last login is considered inactive')
@click.pass_obj
def list_inactive(obj, days, null=False):
    """List inacitve users.

    WARNING! THIS IS NOT OFFICIALLY SUPPORTED BY FLOWDOCK API!

    Users are considered if they haven't used the Flowdock organization during
    last 90 days (customizable, see --days).

    By passing option --null list users who have not been active at all or the
    last time was before flowdock started collecting statistics.
    """
    click.secho("WARNING! This method is not supported by Flowdock!",
                bold=True, fg='red')

    if null:
        click.echo("Listing users that have not been active at all")
    else:
        click.echo("Listing users who have not been active during last {} days"
                   .format(days))

    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    orgs = f.list_organizations()
    for org in orgs:
        inactive = f.find_inactive_in_org(org['parameterized_name'], days, null)
        if len(inactive) > 0:
            click.echo(org['name'])
            for user in inactive:
                click.echo("    {}, {}".format(user['email'], user['accessed_at']))

    f.close()


def print_org(org):
    click.echo(
        'Name: {name}, parameterized name: {parameterized_name}, users: {user_len}'
        .format(user_len=len(org['users']), **org))


def main():
    """Start the cli interface.

    This function is called from the entrypoint script installed by setuptools.
    """
    cli(obj={}, auto_envvar_prefix='FLOWDOCK')


# Allow running this file as standalone app without setuptools wrappers
if __name__ == '__main__':
    main()
