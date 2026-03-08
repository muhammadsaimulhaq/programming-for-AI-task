import requests
import random
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# HTML template as string (no separate file needed)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jokes & Quotes Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            padding: 40px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #4a3f96;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .tabs {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
            color: #4a3f96;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .tab-btn.active {
            background: #764ba2;
            color: white;
            transform: scale(1.05);
        }
        
        .content-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 40px;
            border-radius: 20px;
            margin: 20px 0;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            position: relative;
            transition: all 0.5s;
        }
        
        .content-card:hover {
            transform: translateY(-5px);
        }
        
        .joke-text {
            font-size: 1.3em;
            line-height: 1.6;
            color: #333;
            margin-bottom: 20px;
        }
        
        .joke-type {
            background: #764ba2;
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            margin: 10px 0;
        }
        
        .quote-author {
            font-size: 1.2em;
            color: #764ba2;
            margin-top: 15px;
            font-style: italic;
        }
        
        .reactions {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            justify-content: center;
        }
        
        .reaction-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: 0.3s;
            font-size: 1.1em;
        }
        
        .like-btn {
            background: #d4edda;
            color: #155724;
        }
        
        .like-btn:hover {
            background: #c3e6cb;
        }
        
        .dislike-btn {
            background: #f8d7da;
            color: #721c24;
        }
        
        .dislike-btn:hover {
            background: #f5c6cb;
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 30px 0;
        }
        
        .action-btn {
            padding: 15px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s;
            background: #4a3f96;
            color: white;
            box-shadow: 0 5px 15px rgba(74, 63, 150, 0.3);
        }
        
        .action-btn:hover {
            background: #6359b0;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(74, 63, 150, 0.4);
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #764ba2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .emoji-bg {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .stats {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            color: #666;
        }
        
        .category-tag {
            background: #4a3f96;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .error-msg {
            color: #dc3545;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>😂 Jokes & Quotes Hub</h1>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('jokes')">Jokes</button>
            <button class="tab-btn" onclick="switchTab('quotes')">Quotes</button>
            <button class="tab-btn" onclick="switchTab('facts')">Fun Facts</button>
        </div>
        
        <div class="content-card" id="contentCard">
            <div class="emoji-bg" id="emoji">😄</div>
            <div class="joke-text" id="content">Click below to get started!</div>
            <div class="joke-type" id="contentType"></div>
            <div class="quote-author" id="author"></div>
            <div class="stats" id="stats"></div>
            
            <div class="reactions">
                <button class="reaction-btn like-btn" onclick="react('like')">
                    <span>👍</span> <span id="likes">0</span>
                </button>
                <button class="reaction-btn dislike-btn" onclick="react('dislike')">
                    <span>👎</span> <span id="dislikes">0</span>
                </button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>
        
        <div class="action-buttons">
            <button class="action-btn" onclick="getContent()">
                <span id="actionEmoji">😄</span> Get New
            </button>
        </div>
        
        <div style="text-align: center; color: #666; margin-top: 20px;">
            <p id="currentTime"></p>
        </div>
    </div>
    
    <script>
        let currentTab = 'jokes';
        let currentLikes = 0;
        let currentDislikes = 0;
        
        function switchTab(tab) {
            currentTab = tab;
            
            // Update active tab
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update emoji
            const emojis = {
                'jokes': '😂',
                'quotes': '💭',
                'facts': '🤔'
            };
            document.getElementById('emoji').textContent = emojis[tab];
            document.getElementById('actionEmoji').textContent = emojis[tab];
            
            // Get new content
            getContent();
        }
        
        async function getContent() {
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('contentCard').style.opacity = '0.5';
            
            let url = '';
            switch(currentTab) {
                case 'jokes':
                    url = '/get-joke';
                    break;
                case 'quotes':
                    url = '/get-quote';
                    break;
                case 'facts':
                    url = '/get-fact';
                    break;
            }
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                document.getElementById('contentCard').style.opacity = '1';
                
                // Update content based on tab
                if (currentTab === 'jokes') {
                    document.getElementById('content').textContent = data.joke;
                    document.getElementById('contentType').textContent = data.type || 'Random Joke';
                    document.getElementById('author').textContent = '';
                    currentLikes = data.likes || Math.floor(Math.random() * 1000);
                    currentDislikes = data.dislikes || Math.floor(Math.random() * 100);
                    
                    document.getElementById('stats').innerHTML = `
                        <span class="category-tag">${data.type || 'Joke'}</span>
                    `;
                } else if (currentTab === 'quotes') {
                    document.getElementById('content').textContent = `"${data.text}"`;
                    document.getElementById('contentType').textContent = data.category;
                    document.getElementById('author').textContent = `— ${data.author}`;
                    currentLikes = Math.floor(Math.random() * 800) + 200;
                    currentDislikes = Math.floor(Math.random() * 50);
                    
                    document.getElementById('stats').innerHTML = `
                        <span class="category-tag">${data.category}</span>
                    `;
                } else if (currentTab === 'facts') {
                    document.getElementById('content').textContent = data.fact;
                    document.getElementById('contentType').textContent = data.category;
                    document.getElementById('author').textContent = '';
                    currentLikes = Math.floor(Math.random() * 600) + 100;
                    currentDislikes = Math.floor(Math.random() * 30);
                    
                    document.getElementById('stats').innerHTML = `
                        <span class="category-tag">${data.category}</span>
                    `;
                }
                
                document.getElementById('likes').textContent = currentLikes;
                document.getElementById('dislikes').textContent = currentDislikes;
                
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('contentCard').style.opacity = '1';
                document.getElementById('content').textContent = 'Oops! Something went wrong. Try again!';
            }
        }
        
        function react(type) {
            if (type === 'like') {
                currentLikes++;
                document.getElementById('likes').textContent = currentLikes;
                showNotification('Thanks for liking! 👍');
            } else {
                currentDislikes++;
                document.getElementById('dislikes').textContent = currentDislikes;
                showNotification('Thanks for your feedback!');
            }
        }
        
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #4a3f96;
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                animation: slideIn 0.3s;
                z-index: 1000;
            `;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 2000);
        }
        
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = 
                `🕐 ${now.toLocaleTimeString()} • ${now.toLocaleDateString()}`;
        }
        
        // Load initial content and start timer
        window.onload = () => {
            getContent();
            updateTime();
            setInterval(updateTime, 1000);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get-joke')
def get_joke():
    try:
        # Try joke API
        try:
            response = requests.get('https://v2.jokeapi.dev/joke/Any?type=twopart', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if 'setup' in data:
                    return jsonify({
                        'joke': f"{data['setup']} - {data['delivery']}",
                        'type': data['category'] + ' Joke',
                        'likes': random.randint(100, 1000),
                        'dislikes': random.randint(10, 100)
                    })
        except:
            pass
        
        # Fallback jokes
        fallback_jokes = [
            {
                'joke': "Why don't scientists trust atoms? Because they make up everything!",
                'type': 'Science Joke',
                'likes': 567,
                'dislikes': 23
            },
            {
                'joke': "What do you call a fake noodle? An impasta!",
                'type': 'Food Joke',
                'likes': 432,
                'dislikes': 45
            },
            {
                'joke': "Why did the scarecrow win an award? He was outstanding in his field!",
                'type': 'Dad Joke',
                'likes': 789,
                'dislikes': 67
            },
            {
                'joke': "How does a penguin build its house? Igloos it together!",
                'type': 'Animal Joke',
                'likes': 654,
                'dislikes': 32
            },
            {
                'joke': "What's the best thing about Switzerland? I don't know, but the flag is a big plus!",
                'type': 'Geography Joke',
                'likes': 543,
                'dislikes': 21
            }
        ]
        
        return jsonify(random.choice(fallback_jokes))
        
    except Exception as e:
        return jsonify({
            'joke': "Why did the programmer quit his job? Because he didn't get arrays!",
            'type': 'Programming Joke',
            'likes': 1234,
            'dislikes': 56
        })

@app.route('/get-quote')
def get_quote():
    quotes = [
        {
            'text': "The only way to do great work is to love what you do.",
            'author': "Steve Jobs",
            'category': "Inspirational"
        },
        {
            'text': "Life is what happens when you're busy making other plans.",
            'author': "John Lennon",
            'category': "Life"
        },
        {
            'text': "The future belongs to those who believe in the beauty of their dreams.",
            'author': "Eleanor Roosevelt",
            'category': "Dreams"
        },
        {
            'text': "Success is not final, failure is not fatal: it is the courage to continue that counts.",
            'author': "Winston Churchill",
            'category': "Success"
        },
        {
            'text': "The only impossible journey is the one you never begin.",
            'author': "Tony Robbins",
            'category': "Motivation"
        },
        {
            'text': "Code is like humor. When you have to explain it, it's bad.",
            'author': "Cory House",
            'category': "Programming"
        },
        {
            'text': "Be the change that you wish to see in the world.",
            'author': "Mahatma Gandhi",
            'category': "Inspirational"
        }
    ]
    
    return jsonify(random.choice(quotes))

@app.route('/get-fact')
def get_fact():
    facts = [
        {
            'fact': "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs that's still edible!",
            'category': "Food"
        },
        {
            'fact': "Octopuses have three hearts and blue blood!",
            'category': "Animals"
        },
        {
            'fact': "A day on Venus is longer than a year on Venus.",
            'category': "Space"
        },
        {
            'fact': "Bananas are technically berries, while strawberries aren't!",
            'category': "Food"
        },
        {
            'fact': "The first computer bug was an actual moth found in a computer in 1947.",
            'category': "Technology"
        },
        {
            'fact': "A cloud weighs around a million tonnes.",
            'category': "Science"
        },
        {
            'fact': "The shortest war in history lasted only 38 minutes.",
            'category': "History"
        }
    ]
    
    return jsonify(random.choice(facts))

if __name__ == '__main__':
    print("🚀 Jokes & Quotes App is running!")
    print("📍 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)