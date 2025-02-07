from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Journal entry model stored in table "journal_entries"
class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/api/entries', methods=['GET'])
def get_entries():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400
    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.timestamp.desc()).all()
    data = [{
        'id': entry.id,
        'user_id': entry.user_id,
        'content': entry.content,
        'timestamp': entry.timestamp.isoformat()
    } for entry in entries]
    return jsonify(data)

@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')
    if not user_id or not content:
        return jsonify({'error': 'user_id and content are required'}), 400
    entry = JournalEntry(user_id=user_id, content=content)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Entry added', 'entry_id': entry.id})

@app.route('/api/entries/<int:entry_id>', methods=['PUT'])
def edit_entry(entry_id):
    entry = JournalEntry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({'error': 'content is required'}), 400
    entry.content = content
    db.session.commit()
    return jsonify({'message': 'Entry updated'})

@app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entry = JournalEntry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True) 