import json
import plotly
import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from sklearn.externals import joblib
from sqlalchemy import create_engine


app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens

# load data
engine = create_engine('sqlite:///../data/YourDatabaseName.db')
df = pd.read_sql_table('YourTableName', engine)

# load model
model = joblib.load("../models/your_model_name.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    
   # genre names
    genre_names = list(genre_counts.index)

    # proportion based on
    cat_p = df[df.columns[4:]].sum() / len(df)

    # categories
    # largest bar will be
    cat_p = cat_p.sort_values(ascending=False)

    # on left
    # category names
    cats = list(cat_p.index)

    # will contain all
    words_with_repetition = []

    # words words with
    # repetition
    for text in df['message'].values:
        tokenized_ = tokenize(text)
        words_with_repetition.extend(tokenized_)

    word_count_dict = Counter(words_with_repetition)  # dictionary

    # containing word
    # count for all words
    sorted_word_count_dict = dict(sorted(word_count_dict.items(),
                                         key=operator.itemgetter(1),
                                         reverse=True))  # sort dictionary by\
    # values
    top, top_10 = 0, {}

    for k, v in sorted_word_count_dict.items():
        top_10[k] = v
        top += 1
        if top == 10:
            break
    words = list(top_10.keys())
    pprint(words)
    count_props = 100 * np.array(list(top_10.values())) / df.shape[0]
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    figures = [
        {
            'data': [
                Bar(
                    x=genre_names,
                    y=genre_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        },
        {
            'data': [
                Bar(
                    x=cats,
                    y=cat_p
                )
            ],

            'layout': {
                'title': 'Proportion of Messages <br> by Category',
                'yaxis': {
                    'title': "Proportion",
                    'automargin': True
                },
                'xaxis': {
                    'title': "Category",
                    'tickangle': -40,
                    'automargin': True
                }
            }
        },
        {
            'data': [
                Bar(
                    x=words,
                    y=count_props
                )
            ],

            'layout': {
                'title': 'Frequency of top 10 words <br> as percentage',
                'yaxis': {
                    'title': 'Occurrence<br>(Out of 100)',
                    'automargin': True
                },
                'xaxis': {
                    'title': 'Top 10 words',
                    'automargin': True
                }
            }
        }
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
