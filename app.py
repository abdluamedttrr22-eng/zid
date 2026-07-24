from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zad_kitchen_full.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# جدول الوجبات في المنيو
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String(20), default='حسب الطلب')
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

# جدول الطلبات الواردة
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.Text, nullable=False)
    meal_details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='قيد المعالجة')

with app.app_context():
    db.create_all()

# الصفحة الرئيسية والمنيو
@app.route('/zad-kitchen/menu')
def zad_menu():
    meals = Meal.query.all()
    phone_number = "+9647XXXXXXXXX" # رقم الهاتف الخاص بك
    return render_template('menu.html', meals=meals, phone_number=phone_number)

# إضافة وجبة جديدة
@app.route('/zad-kitchen/add', methods=['GET', 'POST'])
def add_meal():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        price = request.form.get('price')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        
        if title and category and ingredients:
            new_meal = Meal(title=title, category=category, price=price, ingredients=ingredients, instructions=instructions)
            db.session.add(new_meal)
            db.session.commit()
            return redirect(url_for('zad_menu'))
    return render_template('add_meal.html')

# تعديل وجبة
@app.route('/zad-kitchen/edit/<int:id>', methods=['GET', 'POST'])
def edit_meal(id):
    meal = Meal.query.get_or_404(id)
    if request.method == 'POST':
        meal.title = request.form.get('title')
        meal.category = request.form.get('category')
        meal.price = request.form.get('price')
        meal.ingredients = request.form.get('ingredients')
        meal.instructions = request.form.get('instructions')
        db.session.commit()
        return redirect(url_for('zad_menu'))
    return render_template('edit_meal.html', meal=meal)

# حذف وجبة
@app.route('/zad-kitchen/delete/<int:id>')
def delete_meal(id):
    meal = Meal.query.get_or_404(id)
    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for('zad_menu'))

# صفحة تقديم الطلب للزباين
@app.route('/zad-kitchen/order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        meal_details = request.form.get('meal_details')
        
        if customer_name and phone and address:
            new_order = Order(customer_name=customer_name, phone=phone, address=address, meal_details=meal_details)
            db.session.add(new_order)
            db.session.commit()
            return redirect(url_for('order_success'))
    return render_template('order.html')

@app.route('/zad-kitchen/order-success')
def order_success():
    return render_template('order_success.html')

# لوحة التحكم للطلبات الواردة
@app.route('/zad-kitchen/admin/orders')
def admin_orders():
    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
