

# import libraries
import numpy as np
import pandas as pd
import pickle
import flask
from flask import render_template, flash
import plotly.offline as py
from plotly import graph_objs as go
from elasticsearch import Elasticsearch


app = flask.Flask(__name__)

# load data for hotel analyzer
hotel_tone_data = pd.read_csv('../../data/processed_data/hotels_norm_tone.csv', index_col=0)
# load data for hotel indexer
with open ('../../data/processed_data/hotels_docs', 'rb') as fp:
    hotels_docs = pickle.load(fp)

# home page
@app.route('/')
def index():
    return render_template('index.html')

# hotels analyzer
@app.route('/tone', methods=['POST', 'GET'])
def hotel_tone():
    '''Function to get and plot normalized score for given hotel (review text tones and review title tones)'''

    if flask.request.method == 'POST':

        #Gets hotel name using the HTML form
        inputs = flask.request.form
        hotel_name = inputs['hotel']

        # get hotel normalized score
        hotel_tone = pd.Series(hotel_tone_data[hotel_tone_data.name == hotel_name].iloc[:,1:].to_dict(orient='records')[0])

        # plot tones
        fig = go.Figure(data=[
        go.Bar(name='Review Text Tones', x=[i.replace('review_','') for i in hotel_tone.index[:7]], y=hotel_tone.values[:7]),
        go.Bar(name='Review Title Tones', x=[i.replace('review_','') for i in hotel_tone.index[:7]], y=hotel_tone.values[7:])])

        # Change the bar mode
        fig.layout.update(barmode='group')
        first_plot_url = py.plot(fig,filename='templates/tone', auto_open=False)

        return render_template('tone.html')

# hotels indexer
@app.route('/indexer', methods=['POST'])
def hotel_indexer():
    '''Function to store hotels docs in index called 'hotelreview' and give each doc an Id'''

    # create ES object
    es=Elasticsearch([{'host':'localhost','port':9200}])

    # start doc ids with 1
    id_ = 1
    for doc in hotels_docs: # loop over list of hotels docs
        res = es.index(index='hotelreview',doc_type='hotel',id=id_,body=doc)
        id_ += 1

    # return how many doc we have stored using ES
    return render_template('index.html', value=str(id_)+' hotels docs have been indexed')




if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)
