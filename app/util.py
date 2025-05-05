import flask

def make_module_blueprints(name: str) -> tuple[flask.Blueprint, flask.Blueprint]:
    def __make(n: str):
        prefix = "/" + name
        return flask.Blueprint(n, __name__, url_prefix=prefix)
    return __make(name), __make(name)