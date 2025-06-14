#import argparse
from app import app
from dotenv import load_dotenv
import os

@app.route('/', methods=['GET'])
def index():
    return (f"Hello, {os.getenv('APP_ENV')} is running - Version 1.0.0")

if __name__ == '__main__':
    # Parse command line arguments

    # Load environment variables based on the specified environment
    env_file = '.env'
    dotenv_path = os.path.join(os.path.dirname(__file__), env_file)
    load_dotenv(dotenv_path)
    load_dotenv(dotenv_path + "." + os.getenv('APP_ENV'))
    print(f"Starting env --- {os.getenv('APP_ENV')} service on port --- {os.getenv('PORT')}")
    

    # Run the Flask application
    DEBUG = False
    # if os.getenv('APP_ENV') != 'production':
    #     DEBUG = True
        
    app.run(debug=DEBUG, port=os.getenv('PORT'), host='0.0.0.0')
