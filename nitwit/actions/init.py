from nitwit.storage import categories, tags, tickets, lists
from nitwit.helpers import settings as settings_mod
from nitwit.helpers import util
from nitwit import hooks

import random, os, git, configparser, shutil, re


def handle_init( settings ):
    if (dir := settings_mod.find_git_dir()) is None:
        return "Couldn't find a valid git repo"

    directory = None

    # Write out the config values
    cw = git.Repo(dir).config_writer()
    for option, default, func in settings_mod.CONF:
        if option == 'directory':
            directory = default
        cw.set_value(settings_mod.NAMESPACE, option, default)
    cw.release()

    # Write out the global
    config = configparser.ConfigParser()
    config['DEFAULT'] = {k: v for k, v, _ in settings_mod.GLOBAL_CONF}
    with open(f'{dir}/{directory}/config', "w") as handle:
        config.write( handle )

    # Now we can pull our settings_mod and it should have valid data
    if (conf := settings_mod.load_settings()) is None:
        return "Couldn't load settings_mod after initial attempt in Git repo"

    # Setup the default categories
    cats = []
    for name, accepted, visible, parent in settings_mod.CATEGORIES:
        cat = categories.Category()
        cat.name = name
        cat.accepted = accepted
        cat.visible = visible
        cat.parent = parent
        cats.append( cat )

    # Setup the default categories
    ts = []
    for name in settings_mod.TAGS:
        tag = tags.Tag()
        tag.name = name
        ts.append( tag )

    # Write out all the files
    categories.export_categories( conf, cats )
    tags.export_tags( conf, ts )
    tickets.export_tickets( conf, [] )
    lists.export_lists( conf, [] )

    # Copy the hooks
    hook_dir = re.sub('/[^/]+$', '', hooks.__file__)
    for hook in ('prepare-commit-msg', ):
        print(f"Installed hook {hook}")
        shutil.copy(f"{hook_dir}/{hook}", f"{dir}/.git/hooks/{hook}")

    print( f"Initialized nitwit configuration into Git repository in {dir}/.git")

    return None


