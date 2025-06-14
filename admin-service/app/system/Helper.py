from flask import jsonify
class Res:       
    def res(self, data=None, status_code=200):
        # Check if the first argument is JSON-like
        if isinstance(data, (dict, list)):
            # If it's a dictionary or a list, jsonify it and return Response object
            return jsonify(data), status_code
        elif isinstance(data, str):
            # If it's a string, create a JSON object based on the status code
            if status_code in [200, 201]:
                return jsonify({'status': 'success', 'msg': data}), status_code
            else:
                print(f"==>> {{'status': 'error', 'error': data}}")
                return jsonify({'status': 'error', 'error': data}), status_code
        return status_code
    