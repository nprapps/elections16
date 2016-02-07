import app_config
app_config.configure_targets('test')

from fabfile import data
data.bootstrap_db()
