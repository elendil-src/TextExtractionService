import os
import boto3
import json


class Statement:
    """ Represents a statement (credit card, bank etc). Operations are to construct this image from an image, and then
     extract statement as lines of text.
    Prequisite is that the calling context has an AWS access key to AWS Service 'Textract' for the current region."""

    def __init__(self, statement_image_stream):
        """ statement_image_stream - byte array of image.
        Prequisite is that the calling context has an AWS access key to AWS Service 'Textract' for the current
         region."""
        self.statement_image_stream = statement_image_stream
        self.textract_client = boto3.client('textract')

    def process_image(self):
        """Processes image that object was constructed with. Returns list text strings representing lines
        from the statement"""
        # Call Amazon Textract
        response = self.textract_client.detect_document_text(Document={'Bytes': self.statement_image_stream})

        # Textract is poor at analysing image with text in a certain tabular form; it either creates each cell as a
        # line (using line analysis) or a couple of lines in each cell (using table analysis).
        # So this is solved by using line analysis to extract the text, and then checking the X coordinate of the
        # polygon of each line, using the rule that each subsequent 'line' is a cell on the same line will have a larger
        # X coordinate increases value than the last. A new line will be started when the next cell's X coordinate
        # is less than the proceeding line. The proxy for the X coordinate is the Geometry.BoundingBox.Left value.
        # THis is not perfect - depending on quality of image, lines slope that Textract
        # will get the sequence incorrect, ordering the cells out of sequence.
        preceding_cell_x_location = 0
        statement_lines = list()
        current_line = str()

        f = open('textract.json', 'wt')
        f.write(json.dumps(response, indent=4))
        print(json.dumps(response, indent=4) )
#        f.write(json.loads(response).dumps())
        f.close()
        # for item in response["Blocks"]:
        #     if item["BlockType"] == "LINE":
        #         cell_text = item["Text"]
        #         print('\033[94m' + item["Text"] + '\033[0m')
        #         print(item["Geometry"])
        #         cell_x_location = item["Geometry"]["BoundingBox"]["Left"]
        #         #print(cell_x_location)
        #         if (cell_x_location > preceding_cell_x_location):
        #             # this cell is on current line
        #             current_line = current_line + " "
        #         else:
        #             # this cell starts a new line
        #             statement_lines.append(current_line)
        #             current_line = ""
        #
        #         current_line = current_line + cell_text
        #         preceding_cell_x_location = cell_x_location
        #
        # for line in statement_lines:
        #     print(line)


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    #print(__name__)
    statement_image_file = "../ird-test-halifax-cc-statement.jpg"

    # Read document content
    with open(statement_image_file, 'rb') as document:
        image_bytes = bytearray(document.read())

    s = Statement(image_bytes)
    s.process_image()


if __name__ == "__main__":
    main()
