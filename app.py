import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zad_kitchen_single.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# جدول الوجبات
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String(20), default='حسب الطلب')
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

# جدول الطلبات
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.Text, nullable=False)
    meal_details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='قيد المعالجة')

with app.app_context():
    db.create_all()

# قالب HTML الرئيسي المدمج مع الشعار المباشر ورقم الهاتف
LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مطبخ زاد - البصرة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f8f9fa; }
        .navbar-brand img { width: 45px; height: 45px; border-radius: 50%; object-fit: cover; margin-left: 10px; border: 2px solid #ffc107; }
        .card { border-radius: 12px; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); }
        .whatsapp-float { position: fixed; bottom: 20px; left: 20px; z-index: 1000; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/zad-kitchen/menu">
                <!-- شعار مطبخ زاد المباشر -->
                <img src="https://raw.githubusercontent.com/abduhamedttrr22-eng/zad/main/IMG-20260719-WA0009.jpg" alt="شعار مطبخ زاد">
                <span class="fw-bold fs-4">مطبخ زاد</span>
            </a>
            <div class="ms-auto d-flex gap-2">
                <a href="/zad-kitchen/order" class="btn btn-warning fw-bold"><i class="fas fa-shopping-cart"></i> اطلب الآن</a>
                <a href="/zad-kitchen/add" class="btn btn-success"><i class="fas fa-plus"></i> إضافة وجبة</a>
                <a href="/zad-kitchen/admin/orders" class="btn btn-info text-white"><i class="fas fa-clipboard-list"></i> الطلبات</a>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        {{ content | safe }}
    </div>

    <!-- زر الواتساب العائم مع رقم الهاتف -->
    <div class="whatsapp-float">
        <a href="https://wa.me/9647838021664" target="_blank" class="btn btn-success btn-lg rounded-circle shadow" title="تواصل عبر الواتساب">
            <i class="fab fa-whatsapp"></i>
        </a>
    </div>
</body>
</html>
"""

# صفحة المنيو الرئيسي
@app.route('/zad-kitchen/menu')
def zad_menu():
    meals = Meal.query.all()
    html_content = """
        <div class="text-center mb-5">
            <h1 class="text-primary fw-bold">قائمة وجبات مطبخ زاد</h1>
            <p class="text-muted">أكل صحي ولذيذ يوصلك أينما كنت في البصرة</p>
            <a href="https://maps.google.com/?q=Basra,Iraq" target="_blank" class="btn btn-outline-danger mt-2">
                <i class="fas fa-map-marker-alt"></i> موقعنا / توصيل البصرة (GPS)
            </a>
        </div>
        <div class="row">
            {% if meals %}
                {% for meal in meals %}
                <div class="col-md-4 mb-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="card-title text-dark fw-bold mb-0">{{ meal.title }}</h5>
                                <span class="badge bg-secondary">{{ meal.category }}</span>
                            </div>
                            <p class="text-success fw-bold">السعر: {{ meal.price }}</p>
                            <hr>
                            <p class="card-text"><strong>المكونات:</strong> <br>{{ meal.ingredients }}</p>
                            <p class="card-text"><strong>التحضير:</strong> <br>{{ meal.instructions }}</p>
                        </div>
                        <div class="card-footer bg-transparent d-flex justify-content-between">
                            <a href="/zad-kitchen/edit/{{ meal.id }}" class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i> تعديل</a>
                            <a href="/zad-kitchen/delete/{{ meal.id }}" class="btn btn-sm btn-outline-danger" onclick="return confirm('هل أنت متأكد من الحذف؟')"><i class="fas fa-trash"></i> حذف</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="col-12 text-center py-5">
                    <p class="text-muted fs-5">لا توجد وجبات مضافة حالياً في المنيو.</p>
                </div>
            {% endif %}
        </div>
    """
    return render_template_string(LAYOUT, content=render_template_string(html_content, meals=meals))

# صفحة إضافة وجبة
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
            
    html_content = """
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-sm p-4">
                    <h2 class="mb-4 text-center text-success">إضافة وجبة جديدة</h2>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">اسم الوجبة</label>
                            <input type="text" class="form-control" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">التصنيف (فطور، غداء، عشاء...)</label>
                            <input type="text" class="form-control" name="category" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">السعر</label>
                            <input type="text" class="form-control" name="price" value="حسب الطلب">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">المكونات</label>
                            <textarea class="form-control" name="ingredients" rows="3" required></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">طريقة التحضير</label>
                            <textarea class="form-control" name="instructions" rows="3"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">حفظ الوجبة</button>
                    </form>
                    <div class="text-center mt-3">
                        <a href="/zad-kitchen/menu" class="text-decoration-none">العودة إلى المنيو</a>
                    </div>
                </div>
            </div>
        </div>
    """
    return render_template_string(LAYOUT, content=html_content)

# صفحة تعديل وجبة
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
        
    html_content = """
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-sm p-4">
                    <h2 class="mb-4 text-center text-primary">تعديل الوجبة</h2>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">اسم الوجبة</label>
                            <input type="text" class="form-control" name="title" value="{{ meal.title }}" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">التصنيف</label>
                            <input type="text" class="form-control" name="category" value="{{ meal.category }}" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">السعر</label>
                            <input type="text" class="form-control" name="price" value="{{ meal.price }}">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">المكونات</label>
                            <textarea class="form-control" name="ingredients" rows="3" required>{{ meal.ingredients }}</textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">طريقة التحضير</label>
                            <textarea class="form-control" name="instructions" rows="3">{{ meal.instructions }}</textarea>
                        </div>
                        <button type="submit" class="btn btn-success w-100">تحديث الوجبة</button>
                    </form>
                    <div class="text-center mt-3">
                        <a href="/zad-kitchen/menu" class="text-decoration-none">العودة إلى المنيو</a>
                    </div>
                </div>
            </div>
        </div>
    """
    return render_template_string(LAYOUT, content=render_template_string(html_content, meal=meal))

# حذف وجبة
@app.route('/zad-kitchen/delete/<int:id>')
def delete_meal(id):
    meal = Meal.query.get_or_404(id)
    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for('zad_menu'))

# صفحة تقديم الطلب للزبائن
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
            
    html_content = """
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-sm p-4">
                    <h2 class="mb-4 text-center text-dark">نموذج طلب وجبة</h2>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">اسم الزبون الكريم</label>
                            <input type="text" class="form-control" name="customer_name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">رقم الهاتف</label>
                            <input type="text" class="form-control" name="phone" required placeholder="07XXXXXXXXX">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">العنوان بالتفصيل (في البصرة)</label>
                            <textarea class="form-control" name="address" rows="2" required placeholder="مثال: البصرة - الجزائر..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">تفاصيل الطلب والوجبات</label>
                            <textarea class="form-control" name="meal_details" rows="3" required placeholder="اكتب الوجبات المطلوبة..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-warning w-100 fw-bold">إرسال الطلب الآن</button>
                    </form>
                    <div class="text-center mt-3">
                        <a href="/zad-kitchen/menu" class="text-decoration-none">العودة إلى المنيو</a>
                    </div>
                </div>
            </div>
        </div>
    """
    return render_template_string(LAYOUT, content=html_content)

@app.route('/zad-kitchen/order-success')
def order_success():
    html_content = """
        <div class="row justify-content-center text-center">
            <div class="col-md-6">
                <div class="card shadow-sm p-5">
                    <h1 class="text-success mb-3">تم استلام طلبك بنجاح! 🎉</h1>
                    <p class="fs-5 text-muted">شكراً لطلبك من مطبخ زاد. سيتم التواصل معك قريباً للتوصيل.</p>
                    <a href="/zad-kitchen/menu" class="btn btn-primary mt-3">العودة إلى المنيو الرئيسي</a>
                </div>
            </div>
        </div>
    """
    return render_template_string(LAYOUT, content=html_content)

# لوحة التحكم لعرض الطلبات
@app.route('/zad-kitchen/admin/orders')
def admin_orders():
    orders = Order.query.all()
    html_content = """
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="text-primary">لوحة تحكم الطلبات الواردة</h2>
            <a href="/zad-kitchen/menu" class="btn btn-secondary">العودة للمنيو</a>
        </div>
        <div class="card shadow-sm p-3">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>رقم الطلب</th>
                        <th>اسم الزبون</th>
                        <th>الهاتف</th>
                        <th>العنوان</th>
                        <th>الطلب</th>
                        <th>الحالة</th>
                    </tr>
                </thead>
                <tbody>
                    {% if orders %}
                        {% for order in orders %}
                        <tr>
                            <td>{{ order.id }}</td>
                            <td>{{ order.customer_name }}</td>
                            <td>{{ order.phone }}</td>
                            <td>{{ order.address }}</td>
                            <td>{{ order.meal_details }}</td>
                            <td><span class="badge bg-warning text-dark">{{ order.status }}</span></td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="6" class="text-center text-muted py-4">لا توجد طلبات جديدة حتى الآن.</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    """
    return render_template_string(LAYOUT, content=render_template_string(html_content, orders=orders))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
