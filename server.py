from flask import Flask, request
from flask_restful import Resource, Api

import DataFunctions.Functions as df

app = Flask(__name__)

@app.route('/matches', methods=['GET', 'POST']) 
def matches():

    if request.method == 'POST':
        data = request.json

    else:
        # Get data
        data = df.getInputParagraphs()

        # Preprocess data
        preProcessedData = df.preProcessParagraphs(data)

        # Search
        searchResults = df.search(preProcessedData)

        # Highlight
        result = df.getWordsToHighlight(searchResults)
        return result

    return {}

if __name__ == '__main__':
     app.run(debug=True, port='5002')