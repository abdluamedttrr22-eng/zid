from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zad_kitchen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج جدول الوجبات في قاعدة البيانات
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Meal {self.title}>'

# إنشاء قاعدة البيانات تلقائياً إذا لم تكن موجودة
with app.app_context():
    db.create_all()

# مسار عرض قائمة المنيو (الكل)
@app.route('/zad-kitchen/menu')
def zad_menu():
    meals = Meal.query.all()
    return render_template('menu.html', meals=meals)

# مسار إضافة وجبة جديدة للمنيو
@app.route('/zad-kitchen/add', methods=['GET', 'POST'])
def add_meal():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        
        if title and category and ingredients:
            new_meal = Meal(
                title=title, 
                category=category, 
                ingredients=ingredients, 
                instructions=instructions
            )
            db.session.add(new_meal)
            db.session.commit()
            return redirect(url_for('zad_menu'))
            
    return render_template('add_meal.html')

if __name__ == '__main__':
    app.run(debug=True)
