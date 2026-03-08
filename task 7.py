import requests
import random
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Free useless facts APIs
FACT_APIS = [
    "https://uselessfacts.jsph.pl/random.json?language=en",
    "https://api.chucknorris.io/jokes/random",
    "https://api.kanye.rest",
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Useless Info App</title>
    <style>
        body { 
            font-family: 'Comic Sans MS', cursive, sans-serif; 
            max-width: 700px; 
            margin: 0 auto; 
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { 
            text-align: center; 
            color: #764ba2;
            font-size: 2.5em;
        }
        .info-box {
            background: #f0f0f0;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            min-height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3em;
            text-align: center;
            border: 3px dashed #764ba2;
        }
        .buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        button {
            padding: 15px 30px;
            font-size: 1.1em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: transform 0.3s;
            background: #764ba2;
            color: white;
        }
        button:hover {
            transform: scale(1.1);
        }
        .fact-source {
            color: #666;
            font-size: 0.8em;
            margin-top: 20px;
        }
        .emoji {
            font-size: 3em;
            text-align: center;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤪 Useless Info Generator</h1>
        
        <div class="emoji" id="emoji">🤔</div>
        
        <div class="info-box" id="info">
            Click any button to get useless information!
        </div>
        
        <div class="buttons">
            <button onclick="getUselessFact()">Random Fact</button>
            <button onclick="getChuckNorris()">Chuck Norris</button>
            <button onclick="getKanyeQuote()">Kanye Quote</button>
            <button onclick="getRandomNumber()">Number Fact</button>
            <button onclick="getDogFact()">Dog Fact</button>
            <button onclick="getCatFact()">Cat Fact</button>
        </div>
        
        <p class="fact-source" id="source"></p>
    </div>
    
    <script>
        const emojis = ['🤔', '😮', '🤯', '😄', '🤪', '😎', '🥴', '🤓'];
        
        function changeEmoji() {
            const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
            document.getElementById('emoji').textContent = randomEmoji;
        }
        
        async function getUselessFact() {
            const response = await fetch('/useless-fact');
            const data = await response.json();
            document.getElementById('info').textContent = data.fact;
            document.getElementById('source').textContent = `Source: ${data.source}`;
            changeEmoji();
        }
        
        async function getChuckNorris() {
            const response = await fetch('/chuck-norris');
            const data = await response.json();
            document.getElementById('info').textContent = data.fact;
            document.getElementById('source').textContent = 'Source: Chuck Norris Facts';
            changeEmoji();
        }
        
        async function getKanyeQuote() {
            const response = await fetch('/kanye-quote');
            const data = await response.json();
            document.getElementById('info').textContent = `"${data.fact}" - Kanye West`;
            document.getElementById('source').textContent = 'Source: Kanye Quotes';
            changeEmoji();
        }
        
        async function getRandomNumber() {
            const response = await fetch('/number-fact');
            const data = await response.json();
            document.getElementById('info').textContent = data.fact;
            document.getElementById('source').textContent = 'Source: Numbers API';
            changeEmoji();
        }
        
        async function getDogFact() {
            const response = await fetch('/dog-fact');
            const data = await response.json();
            document.getElementById('info').textContent = data.fact;
            document.getElementById('source').textContent = 'Source: Dog Facts';
            changeEmoji();
        }
        
        async function getCatFact() {
            const response = await fetch('/cat-fact');
            const data = await response.json();
            document.getElementById('info').textContent = data.fact;
            document.getElementById('source').textContent = 'Source: Cat Facts';
            changeEmoji();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/useless-fact')
def useless_fact():
    try:
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        data = response.json()
        return jsonify({
            'fact': data['text'],
            'source': 'Useless Facts API'
        })
    except:
        return jsonify({
            'fact': "A cloud weighs around a million tonnes.",
            'source': 'Fallback Fact'
        })

@app.route('/chuck-norris')
def chuck_norris():
    try:
        response = requests.get("https://api.chucknorris.io/jokes/random")
        data = response.json()
        return jsonify({
            'fact': data['value'],
            'source': 'Chuck Norris API'
        })
    except:
        return jsonify({
            'fact': "Chuck Norris can divide by zero.",
            'source': 'Fallback Fact'
        })

@app.route('/kanye-quote')
def kanye_quote():
    try:
        response = requests.get("https://api.kanye.rest")
        data = response.json()
        return jsonify({
            'fact': data['quote'],
            'source': 'Kanye API'
        })
    except:
        return jsonify({
            'fact': "I'm the greatest artist of all time.",
            'source': 'Fallback Fact'
        })

@app.route('/number-fact')
def number_fact():
    try:
        num = random.randint(1, 1000)
        response = requests.get(f"http://numbersapi.com/{num}")
        return jsonify({
            'fact': response.text,
            'source': 'Numbers API'
        })
    except:
        return jsonify({
            'fact': "42 is the answer to life, the universe, and everything.",
            'source': 'Fallback Fact'
        })

@app.route('/dog-fact')
def dog_fact():
    dog_facts = [
        "Dogs have about 1,700 taste buds.",
        "A dog's nose print is unique, much like a human's fingerprint.",
        "Dogs can understand up to 250 words and gestures.",
        "The Basenji dog doesn't bark, it yodels.",
        "Dogs' sense of smell is 10,000 to 100,000 times better than humans.",
        "A Greyhound could beat a Cheetah in a long distance race.",
        "Dalmatians are born completely white.",
        "Dogs sweat through their paw pads.",
    ]
    return jsonify({
        'fact': random.choice(dog_facts),
        'source': 'Dog Facts Database'
    })

@app.route('/cat-fact')
def cat_fact():
    cat_facts = [
        "Cats sleep for about 70% of their lives.",
        "A group of cats is called a clowder.",
        "Cats can't taste sweetness.",
        "A cat's nose is as unique as a human's fingerprint.",
        "Cats have 32 muscles in each ear.",
        "A cat can jump up to six times its length.",
        "Cats have 230 bones, while humans have 206.",
        "A cat's purr vibrates at a frequency of 25 to 150 hertz.",
    ]
    return jsonify({
        'fact': random.choice(cat_facts),
        'source': 'Cat Facts Database'
    })

if __name__ == '__main__':
    app.run(debug=True)