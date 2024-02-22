from flask import Flask, request, jsonify
from random import choice, randint
from string import ascii_lowercase


app = Flask(__name__)
notes = {}


def generate_random_string(length):
    return ''.join(choice(ascii_lowercase) for _ in range(length))


def generate_random_url():
    protocol = 'http://'
    domain = generate_random_string(randint(5, 10)) + choice(('.com', '.org'))
    path = '/' + generate_random_string(randint(5, 10))
    return f"{protocol}{domain}{path}"


@app.route('/note/', methods=['POST'])
def post_note():
    try:
        data = request.get_json()
        note = data['note']
        # Check if 'note' is empty or contains only whitespace
        if not note.strip():
            return jsonify({"error": "Invalid request format. 'note' field cannot be empty"}), 400

        # Generate a unique URL and store the note
        while True:
            unique_url = generate_random_string(10)
            if unique_url not in notes:
                notes[unique_url] = note
                return jsonify({"message": "Note saved successfully", "note_url": unique_url}), 201

    except KeyError:
        return jsonify({"error": "Invalid request format. 'note' key missing in JSON"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/note/<note_url>/', methods=['GET'])
def get_note(note_url):
    note = notes.get(note_url)
    if note is not None:
        return jsonify({"note": note}), 200
    else:
        return jsonify({"error": "Note not found"}), 404


@app.route('/notes/', methods=['GET'])
def get_all_notes():
    if not notes:
        return jsonify({"message": "There are no notes yet"}), 200
    return jsonify({"notes": notes}), 200


if __name__ == "__main__":
    app.run()
