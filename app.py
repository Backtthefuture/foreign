from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from name_generator import GLMNameGenerator
import traceback
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# 使用相对路径
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'characters.db')
db = SQLAlchemy(app)

# 汉字数据模型
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character = db.Column(db.String(1), unique=True, nullable=False)
    pinyin = db.Column(db.String(10), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    frequency = db.Column(db.Float)
    
# 创建数据库表
with app.app_context():
    db.create_all()

# 创建GLM名字生成器实例
name_generator = GLMNameGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        english_name = request.json.get('name', '').strip()
        if not english_name:
            return jsonify({
                'error': '请输入英文名',
                'names': [{
                    'chinese_name': '李友好',
                    'pinyin': 'lǐ yǒu hǎo',
                    'meaning': '友善和美好的人',
                    'cultural_explanation': '李是常见姓氏，友好表示友善美好之意',
                    'english_explanation': 'A name representing friendliness and kindness'
                }]
            }), 200

        # 使用GLM生成名字
        result = name_generator.generate_names(english_name)
        return jsonify(result), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': '生成名字时出错',
            'message': str(e)
        }), 500

# Vercel需要的应用实例
app.debug = False

if __name__ == '__main__':
    # 本地运行时使用
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5001)))
