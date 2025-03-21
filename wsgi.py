from flask import Flask, render_template, request
from app.src.recommender import CollegeRecommender
import os
import pandas as pd

app = Flask(__name__)
app.static_folder = 'app/static'
app.template_folder = 'app/templates'

recommender = CollegeRecommender()

def get_snippet(college):
    review = college.get('review', '')
    if review:
        words = review.split()
        return ' '.join(words[:50]) + "..." if len(words) > 50 else review
    else:
        return "No review available"

@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    if request.method == 'POST':
        query = request.form.get('query')
        recommendations = recommender.recommend(query).to_dict('records')

        # Enrich each record with the original review for display
        df = pd.read_csv('app/data/processed_colleges.csv')
        results = []
        for rec in recommendations:
            matching_row = df[df['college'] == rec['college']].to_dict('records')
            if matching_row:
                full_record = matching_row[0]  # Get original review
                full_record['rating'] = rec['rating'] # Attach model's rating
                full_record['snippet'] = get_snippet(full_record) #Snippet
                results.append(full_record)

        return render_template('index.html', results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
