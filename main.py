#!/usr/bin/env python3
import sys
import click
from flowdock import Flowdock

# This is the common endpoint for all commands. Handle common options here
@click.group()
@click.option('--debug', default=False, is_flag=True, help='Turn on debug ouptut')
@click.option('--api_key', help='Flowdock API key for the user')
@click.pass_obj
def cli(obj, api_key, debug):
    """Simple command line utility for managing Flowdock

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

@click.command(short_help="List Flowdock organizations")
@click.pass_obj
def list_orgs(obj):
    """List flowdock organizations this user is part of."""
    click.echo("Getting organization list...")
    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    orgs = f.get_organizations()
    f.close()
    for org in orgs:
        print_org(org)

@click.command(short_help="Find user from organisations")
@click.argument('email')
@click.pass_obj
def find_user(obj, email):
    """List the organizations the given user belongs to"""
    click.echo("Listing the organizations {} belongs to".format(email))
    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    user_orgs = f.find_user_orgs(email)
    if len(user_orgs == 0):
        click.echo("User not found!")
    click.echo("User is part of the following Flowdock organizations:")
    for org in user_orgs:
        click.echo(org['name'])


@click.command(short_help="Delete user")
@click.argument('email')
@click.pass_obj
def delete_user(obj, email,):
    """Delete user with given EMAIL address from all Flowdock organizations."""
    click.echo("Deleting user {} from all organizations...".format(email))
    f = Flowdock(obj['APIKEY'], debug=obj['DEBUG'], print_function=click.echo)
    orgs = f.find_user_orgs()
    if len(orgs == 0):
        click.echo("User not found!")
        return
    click.echo("User is part of the following Flowdock organizations:")
    for org in orgs:
        click.echo(org['name'])
    if click.confirm('Are you sure you want to delete user?'):
        __delete_user_from_orgs(f, email, orgs)
        click.echo('Done!')

def __delete_user_from_orgs(flowdock, email, orgs):
    # Get the user object related to the email address
    user = None
    for org_user in orgs[0]['users']:
        if org_user['email'] == email:
            user = org_user
    for org in orgs:
        f.delete_user_from_org(user, org)


@click.command(short_help="List inactive users")
@click.argument('--days', default=90)
@click.pass_obj
def list_inactive(obj, days):
    """Click users that have not signed in to any of your Flowdock organisations
    during last DAYS days.
    """
    click.echo("Not implemented yet!")

def print_org(org):
    click.echo(
        'Name: {name}, parameterized name: {parameterized_name}, users: {user_len}'
        .format(user_len=len(org['users']), **org))

# Add available commands to cli group
cli.add_command(list_orgs)
cli.add_command(find_user)
cli.add_command(delete_user)
cli.add_command(list_inactive)

def main():
    """Start the cli interface.

    This function is called from the entrypoint script installed by setuptools.
    """
    cli(obj={}, auto_envvar_prefix='FLOWDOCK')

if __name__ == '__main__':
    main()
