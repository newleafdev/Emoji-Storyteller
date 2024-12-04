from flask import Flask, render_template, request, jsonify
import random
import ollama
import emoji

app = Flask(__name__)

MODEL = "gemma2:9b"

EMOJIS = ["😀", "😎", "🌟", "🌈", "🌸", "🐶", "🐱", "🦁", "🐯", "🐮", "🐷", "🦊", "🐸", 
          "🐙", "🦋", "🌺", "🌲", "🌍", "⭐", "🌙", "☀️", "🌤", "🌈", "🍎", "🍕", "🎨", 
          "🎭", "🎪", "🎡", "🚗", "✈️", "🚀", "🏰", "🗽", "🎸", "📚", "⚽", "🎮", "🎲"]

EMOJIS = list(emoji.EMOJI_DATA.keys())

SYSTEM_PROMPT = "You are an expert in second language education. You will write stories by considering the given list of emoji and you will place them appropriately in a way that makes it easy to understand. You will write short stories at the CEFR level requested. You will include the provided emoji in your story. You will always write gramatically correct sentences at an appropriate level. Your response should only include the story content as you are producing writing."

LANGUAGE_LEVELS = {
    'A1': 'Beginner - Basic phrases and everyday expressions',
    'A2': 'Elementary - Common expressions and simple descriptions',
    'B1': 'Intermediate - Clear standard input on familiar matters',
    'B2': 'Upper Intermediate - Complex texts and abstract topics'
}

@app.route('/')
def home():
    return render_template('index.html', levels=LANGUAGE_LEVELS)

@app.route('/draw_card', methods=['POST'])
def draw_card():
    emoji = random.choice(EMOJIS)
    return jsonify({'emoji': emoji})

@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()
    emojis = data.get('emojis', [])
    level = data.get('level', 'A1')
    
    if not emojis:
        return jsonify({'error': 'No emojis provided'}), 400
    
    prompt = create_prompt(emojis, level)
    
    try:
        response = ollama.chat(model=MODEL, messages=[
            {'role': 'system','content': SYSTEM_PROMPT},
            {'role': 'user','content': prompt}
        ])
        
        story = response['message']['content']
        return jsonify({'story': story})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_prompt(emojis, level):
    level_prompts = {
        'A1': "Write a very simple story using basic words and short sentences. The story should be about the things depicted by the emoji listed below. Do not use conjunctives (words like and, but, so). Do not use compound sentences. Do not use the past tense. Only use the present tense. Include these emojis: ",
        'A2': "Write a simple story with common words and basic descriptions. The story should be about the things depicted by the emoji listed below. Avoid idiomatic language. You may use the past tense. Avoid compound sentences. Avoid complex sentences. Include these emojis: ",
        'B1': "Write an interesting story with some complex sentences. The story should be about the things depicted by the emoji listed below. Avoid idiomatic language. Include these emojis: ",
        'B2': "Write an interesting story with rich vocabulary and complex structures. The story should be about the things depicted by the emoji listed below. Use idioms lightly. Write at a B2 level, or a level suitable for a native 12 year old. Include these emojis: "
    }
    
    base_prompt = level_prompts[level]
    emoji_text = " ".join(emojis)
    return f"{base_prompt}{emoji_text}"

if __name__ == '__main__':
    app.run(debug=True)