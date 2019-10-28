import os
import base64


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    statement_image_file = "../ird-test-halifax-cc-statement.jpg"

    # Read document content
    with open(statement_image_file, 'rb') as document:
        image_bytes = bytearray(document.read())

    encoded_bytes: str
    encoded_bytes = base64.b64encode(image_bytes)

    #print(str(encoded_bytes))

    decoded_image = base64.b64decode(encoded_bytes, validate=True)

    print('original len='+str(len(image_bytes)) + 'decoded len=' + str(len(decoded_image) )+ ' : b64len='
          + str(len(encoded_bytes)))
    if decoded_image == image_bytes:
        print('decoded matches original')
        opfile_name = statement_image_file + '.b64'
        with open(opfile_name, 'wb') as opfile:
            opfile.write(encoded_bytes)
            opfile.close()
            print('decoded written to:' + opfile_name)
    else:
        print('decoded does not match original:len')


if __name__ == "__main__":
    main()
