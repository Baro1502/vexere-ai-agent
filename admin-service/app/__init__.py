from flask import Flask
from flask_cors import CORS
from flask_helmet import FlaskHelmet
from dotenv import load_dotenv
import os

os.environ["APP_ENV"] = os.getenv('APP_ENV') or 'dev'
# Load environment variables first
env_file = '.env'
dotenv_path = os.path.join(os.path.dirname(__file__), '..', env_file)
load_dotenv(dotenv_path)
load_dotenv(dotenv_path + "." + os.getenv('APP_ENV'))

app = Flask(__name__)
CORS(app)
FlaskHelmet().init_app(app)

# Dynamically import all modules and register their controllers as Blueprints
module_dirs = [d for d in os.listdir(os.path.join(os.path.dirname(__file__), 'modules')) 
               if not d.startswith('__') and os.path.isdir(os.path.join(os.path.dirname(__file__), 'modules', d))]

for module_dir in module_dirs:
    module_files = [f for f in os.listdir(os.path.join(os.path.dirname(__file__), 'modules', module_dir)) 
                            if f.startswith('Controller') and not f.startswith('__')]
    for module_file in module_files:
        module_name = 'app.modules.' + module_dir + '.' + os.path.splitext(module_file)[0]
        module = __import__(module_name, fromlist=['*'])
        controller = getattr(module, 'controller')
        
        print(controller.name)
        controller.add_url_rule(f'/{controller.name}', view_func=controller.create, methods=['POST'])
        controller.add_url_rule(f'/{controller.name}', view_func=controller.get_all, methods=['GET'])
        
        match controller.name:
            case 'vector':
                controller.add_url_rule(f'/{controller.name}/query' , view_func=controller.query, methods=['POST'])

    app.register_blueprint(controller)
