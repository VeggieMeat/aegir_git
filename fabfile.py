from fabric.api import *
import time

env.user = 'aegir'
env.shell = '/bin/bash -c'

# Download and import a platform using Git
def build_platform(site, profile, webserver, dbserver, giturl, gitrepo, gitbranch, build):
  print "===> Building the platform..."
  run("git archive --prefix=/var/aegir/platforms/%s --format=tar --remote=%s:%s %s | tar -xvf -" % (build, giturl, gitrepo, gitbranch))
  run("drush --root=/var/aegir/platforms/%s/ provision-save @platform_%s --web_server=@server_%s --context_type=platform --debug" % (build, build, webserver))
  run("drush @hostmaster hosting-import '@platform_%s'" % build)
  run("drush @hostmaster hosting-dispatch")

# Install a site on a platform, and kick off an import of the site
def install_site(site, profile, webserver, dbserver, giturl, gitrepo, gitbranch, build):
  print "===> Installing the site for the first time..."
  run("drush @%s provision-install --debug" % site)
  run("drush @hostmaster hosting-task @platform_%s verify --debug" % build)
  time.sleep(5)
  run("drush @hostmaster hosting-dispatch --debug")
  time.sleep(5)
  run("drush @hostmaster hosting-task @%s verify --debug" % site)

# Migrate a site to a new platform
def migrate_site(site, profile, webserver, dbserver, giturl, gitrepo, gitbranch, build):
  print "===> Migrating the site to the new platform"
  run("drush @%s provision-migrate @platform_%s --debug" % (site, build))

# Save the Drush alias to reflect the new platform
def save_alias(site, profile, webserver, dbserver, giturl, gitrepo, gitbranch, build):
  print "===> Updating the Drush alias for this site"
  run("drush provision-save @%s --context_type=site --uri=%s --platform=@platform_%s --web_server=@server_%s --db_server=@server_%s --profile=%s --debug" % (site, site, build, webserver, dbserver, profile))

# Import a site into the frontend, so that Aegir learns the site is now on the new platform
def import_site(site, profile, webserver, dbserver, giturl, gitrepo, gitbranch, build):
  print "===> Refreshing the frontend to reflect the site under the new platform"
  run("drush @hostmaster hosting-import @%s --debug" % site)
  run("drush @hostmaster hosting-task @platform_%s verify --debug" % build)
  run("drush @hostmaster hosting-import @%s --debug" % site)
  run("drush @hostmaster hosting-task @%s verify --debug" % site)