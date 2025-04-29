from flask import Flask
from blueprints.weightTrack import bp as weight_bp

def create_app():
    app = Flask(__name__)
    # … load config, init extensions, etc. …

    # register your weightTrack blueprint
    app.register_blueprint(weight_bp)  # mounted at /weight/


    @app.route('/')
    def index():
        return 'Hello, world!'

    return app

if __name__ == '__main__':
    create_app().run(debug=True)