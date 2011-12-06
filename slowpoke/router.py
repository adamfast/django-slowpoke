class SlowPokeDBRouter(object):
    """A router to control all database operations on models in
    the slowpoke application"""

    def db_for_read(self, model, **hints):
        "Point all operations on slowpoke models to 'slowpokelogs'"
        if model._meta.app_label == 'slowpoke':
            return 'slowpokelogs'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on slowpoke models to 'slowpokelogs'"
        if model._meta.app_label == 'slowpoke':
            return 'slowpokelogs'
        return 'default'
