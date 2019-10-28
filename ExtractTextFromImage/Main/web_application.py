import importlib
from flask import Flask, jsonify, request, Response
from io import BytesIO
import base64
import json

# TODO - review module struct/function/var names/logic
# TODO - define correct web responses (200,201, 404)
# TODO - name tests _test_api and test_unit
# TODO - create model
# TODO - unit test model
# TODO - validate data via Model
# TODO - use if key in dict
# TODO - configuration adjust for different envs
# TODO - configuration adjust for privacy/security
# TODO - test api cases non-image, non-document, document etc
# TODO - set types on declartions and methods/functions
# TODO - return location header on Post with location of new resource.


# Module level initialisation
app = Flask(__name__)
s3_mod = importlib.import_module('s3_storage')
error = importlib.import_module('error_response')
image_content = importlib.import_module('image_content')
storage = None


@app.route('/image', methods=['POST'])
def image_create():
    """
    Create a resource representing an image of a document. Returns identity
    of that resource.  Create image in model. Requires binary (jpg?) representing the image.
    Input:
    {
        'image-base64': <base64 rep of the image>
    }
    Returns:
    {
        'image-id': <key as string>
    }
    """
    app.logger.debug('Entered function: image_create()')
    return_body: dict
    return_code: int
    try:
        body_jason = request.get_json()

        result = image_content.image_content_from_dict(body_jason)
        image_b64 = result.image_base64
        image_bytes = base64.b64decode(image_b64, validate=True)
        stream_obj = BytesIO(image_bytes)

        key = storage.file_create(stream_obj)
        return_body = {'image-id': key}
        return_code = 200
    except Exception as e:
        return_body = error.Error('image_post', '', '', str(e)).to_dict()
        return_code = 400

    response = Response(json.dumps(return_body), status=return_code, mimetype='application/json')
    return response


@app.route('/image/<image_id>', methods=['GET'])
def image_get(image_id):
    """
    Return a resource representing an image of a document given the identity of that resource.
    """
    app.logger.debug('Entered function: image_get() for %s', image_id)
    return_body: dict
    return_code: int
    error_msg: str

    try:
        file_contents = storage.file_read(image_id)
        file_base64 = base64.b64encode(file_contents).decode('utf8')
        return_body = {
            'given-image-id': image_id,
            'image-base64': file_base64,
            }
        return_code = 200
    except Exception as e:
        return_body = error.Error('image_get', image_id, '', str(e)).to_dict()
        return_code = 404

    response = Response(json.dumps(return_body), status=return_code, mimetype='application/json')
    return response


@app.before_request
def log_request_info():
    app.logger.debug('Request: %s: %s: %s', request.method,  request.url,  request.headers)

    try:
        if request.is_json:
            json_req = request.get_json()
            app.logger.debug('Body:request.get_json() succeeded')
            app.logger.debug('Body:json headers %s', str(json_req.keys()))
            app.logger.debug('Body:data length %i', len(request.get_data()))
            app.logger.debug('Body-start(Json): %s', json_req['image-base64'][0:79])
            app.logger.debug('Body-end(Json): %s', json_req['image-base64'][-80:])
    except Exception as e:
        app.logger.debug('Body error: %s', e)
        app.logger.debug('Body(raw): %s', request.get_data()[0:80])
    except:
        app.logger.debug('Body - unexpected problem')
        app.logger.debug('Body(raw): %s', request.get_data()[0:80])

    return None


def main():
    app.config.from_object('Config')

    # Load and validate configuration settings
    #    config = yaml.safe_load(open("ExtractTextFromImage.yml"))

    #    listening_port = config.get('listening_port', 5000)

    #    s3_bucket_region = config.get('s3_bucket_region', 'eu-west-2')

    # if 's3_bucket_name' not in config:
    #     raise Exception('ExtractTextFromImage.yml must contain s3_bucket_name attribute')
    # else:
    #     s3_bucket_name = config['s3_bucket_name']

    s3_bucket_region = app.config.get('S3_BUCKET_REGION', 'eu-west-2')

    if 'S3_BUCKET_NAME' not in app.config:
        raise Exception('Config.py must contain S3_BUCKET_NAME attribute')
    else:
        s3_bucket_name = app.config['S3_BUCKET_NAME']

    global storage
    storage = s3_mod.S3Storage(s3_bucket_name, s3_bucket_region)

    # Create storage that will be our Model
    storage.bucket_create_if_not_exist()

    # Setup logging
    # maxBytes to small number, in order to demonstrate the generation of multiple log files (backupCount).

    #   handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    # getLogger(__name__):   decorators loggers to file + werkzeug loggers to stdout
    # getLogger('werkzeug'): decorators loggers to file + nothing to stdout

    #    logger = logging.getLogger(__name__)

    #    logger.addHandler(handler)

    # app.log.addHandler(RotatingFileHandler('log.txt', mode='w'))
    # app.log.setLevel(logging.DEBUG)

    # app.logger.setLevel(logging.DEBUG)
    app.logger.debug('this is a DEBUG message')
    app.logger.debug('Config:\\n' + str(app.config))
    # app.logger.info('this is an INFO message')
    # app.logger.warning('this is a WARNING message')
    # app.logger.error('this is an ERROR message')
    # app.logger.critical('this is a CRITICAL message')

    #    app.run(port=listening_port, debug=True)
    app.run()


if __name__ == "__main__":
    main()
