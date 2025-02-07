from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import requests
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Daily quote model stored in table "daily_quotes"
class DailyQuote(db.Model):
    __tablename__ = 'daily_quotes'
    id = db.Column(db.Integer, primary_key=True)
    quote_date = db.Column(db.String(10), unique=True, nullable=False)  # Format: YYYY-MM-DD
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=True)

with app.app_context():
    db.create_all()

def fetch_external_quote():
    try:
        # With 30% probability, simulate an SSL error by omitting verify=False
        if random.random() < 0.3:
            print("Simulating error: calling API with default SSL verification (verify=True)")
            response = requests.get("https://api.quotable.io/random", timeout=5)
        else:
            response = requests.get("https://api.quotable.io/random", timeout=5, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('content'), data.get('author')
    except Exception as e:
        print("Error fetching external quote:", e)
    # Signal an error by returning None values.
    return None, None

@app.route('/api/daily_quote', methods=['GET'])
def daily_quote():
    today_str = date.today().isoformat()
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    quote = DailyQuote.query.filter_by(quote_date=today_str).first()
    if refresh:
        # Always attempt to update the quote when refresh is requested.
        content, author = fetch_external_quote()
        if content is None:
            return jsonify({
                'error': 'Unable to fetch quote at this moment. Please try again later.'
            }), 500
        if quote:
            quote.content = content
            quote.author = author
        else:
            quote = DailyQuote(quote_date=today_str, content=content, author=author)
            db.session.add(quote)
        db.session.commit()
    elif not quote:
        content, author = fetch_external_quote()
        if content is None:
            return jsonify({
                'error': 'Unable to fetch quote at this moment. Please try again later.'
            }), 500
        quote = DailyQuote(quote_date=today_str, content=content, author=author)
        db.session.add(quote)
        db.session.commit()
    return jsonify({
        'quote_date': quote.quote_date,
        'content': quote.content,
        'author': quote.author
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True) 