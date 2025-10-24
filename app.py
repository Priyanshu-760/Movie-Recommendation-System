import numpy as np
import pandas as pd
from flask import Flask, request, render_template, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import seaborn as sns
import requests
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# OMDB API key
OMDB_API_KEY = "8344faf1"

#Loading and reading the data set into pandas dataframe
df=pd.read_csv("model/movies.csv")

#filtering the columns as per our need
required_column = ["genres", "keywords", "overview", "title", "runtime", "original_language", "tagline", "popularity", "cast"]
#saving the required column into the main dataframe
df = df[required_column]

#28 missing rows in genres
#412 missing rows in keywords
#3 missing rows in overview
#insted of replacing with mean value dropping the null rows and balancing it with other rows
df = df.dropna().reset_index(drop=True)

#creating a new column name combined and combining the genres keywords and overview in it
df['combined'] = df['genres']+' '+ df['keywords']+' '+ df['overview']

#creating a new variable name data with having only the required columns
data = df[['title','combined','genres','keywords', 'overview', 'runtime', 'original_language', 'tagline', 'popularity', 'cast']]

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

#using the stopwords to remove the duplicate values from df
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    #removes special character and numbers from data
    text = re.sub(r"[^a-zA-Z\s]","",text)
    #convert to lower case
    text = text.lower()
    #tokenize and remove stopwards
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

#applying the preprocessing to the movie content
data['cleaned_text']= df['combined'].apply(preprocess_text)

tfidf_vectorizer = TfidfVectorizer(max_features=5000)
#for finding similar vectors like similar movies
tfidf_matrix = tfidf_vectorizer.fit_transform(data['cleaned_text'])

#for calculating the distance between two vectors 
#how much similar are the movies
cosine_sim = cosine_similarity(tfidf_matrix,tfidf_matrix)

# Function to fetch movie details from OMDB API
def fetch_movie_details(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                return {
                    'title': data.get('Title', title),
                    'year': data.get('Year', 'N/A'),
                    'poster': data.get('Poster', ''),
                    'plot': data.get('Plot', 'No description available'),
                    'imdbRating': data.get('imdbRating', 'N/A'),
                    'runtime': data.get('Runtime', 'N/A'),
                    'genre': data.get('Genre', 'N/A')
                }
        return None
    except Exception as e:
        print(f"Error fetching movie details for {title}: {e}")
        return None

#reccomendation script
#reccomendation function
def recommend_movies(movie_name, cosine_sim=cosine_sim, df = data, top_n=6):
    #find the index of the movie
    idx = df[df['title'].str.lower() == movie_name.lower()].index
    if len(idx) == 0:
        return ["Movie not found in the DataSet!"]
    idx = idx[0]

     #get similarity score
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]

    #get movie indices
    movie_indices = [i[0] for i in sim_scores]

    #return top n similar movies with details
    recommended_movies = []
    for i in movie_indices:
        title = df['title'].iloc[i]
        movie_details = fetch_movie_details(title)
        if movie_details:
            recommended_movies.append(movie_details)
        else:
            # Fallback if OMDB API fails
            recommended_movies.append({
                'title': title,
                'year': 'N/A',
                'poster': '',
                'plot': 'No description available',
                'imdbRating': 'N/A',
                'runtime': 'N/A',
                'genre': 'N/A'
            })
    
    return recommended_movies


# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend_api():
    try:
        req = request.get_json()
        movie_title = req.get('movie_title')
        result = recommend_movies(movie_title)
        return jsonify({'recommendations': result})
    except Exception as e:
        return jsonify({'recommendations': [f"Error: {str(e)}"]})

if __name__ == '__main__':
    app.run(debug=True)