from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'horus_technologies_secret_key'

# Configure SQLite Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'horus.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Upload Folder
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'js', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

db = SQLAlchemy(app)

# Gmail SMTP Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jetdonleeisco5@gmail.com'
app.config['MAIL_PASSWORD'] = 'zdnl gcnf kaec pxuc'
app.config['MAIL_DEFAULT_SENDER'] = ('Horus Corporate Portal', 'jetdonleeisco5@gmail.com')

mail = Mail(app)
RECIPIENT_EMAIL = 'jetdonleeisco5@gmail.com'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Product Database Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(100), default='logo (47).jpg')
    status = db.Column(db.String(50), default='OPERATIONAL')
    sla = db.Column(db.String(50), default='99.99% Uptime')
    tech_stack = db.Column(db.String(200), nullable=False)
    features = db.Column(db.Text, nullable=False)
    compliance = db.Column(db.String(100), default='ISO 27001')


# Inquiry Database Model (Stores Client Messages)
class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    db_products = Product.query.all()
    products = []
    for p in db_products:
        products.append({
            "id": p.id,
            "title": p.title,
            "tagline": p.tagline,
            "image": p.image if p.image else 'logo (47).jpg',
            "status": p.status,
            "sla": p.sla,
            "tech_stack": p.tech_stack.split(','),
            "features": p.features.split(','),
            "compliance": p.compliance.split(',')
        })
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == 'jetdonleeisco5@gmail.com' and password == 'horus2026':
            session['user'] = email
            flash("Secure session initialized successfully.", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid corporate credentials provided.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Session terminated securely.", "success")
    return redirect(url_for('home'))


# --- Admin Dashboard (Manages Products & Inquiries) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('user'):
        flash("Unauthorized access. Please sign in.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_tagline = request.form.get('tagline')
        new_tech = request.form.get('tech_stack')
        new_features = request.form.get('features')
        new_sla = request.form.get('sla', '99.99% Uptime')

        image_filename = 'logo (47).jpg'
        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        product = Product(
            title=new_title,
            tagline=new_tagline,
            tech_stack=new_tech,
            features=new_features,
            sla=new_sla,
            image=image_filename
        )
        db.session.add(product)
        db.session.commit()
        flash("New solution published successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    products = Product.query.all()
    inquiries = Inquiry.query.all()
    return render_template('admin.html', products=products, inquiries=inquiries)


# --- Edit Product Route ---
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if not session.get('user'):
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.title = request.form.get('title')
        product.tagline = request.form.get('tagline')
        product.tech_stack = request.form.get('tech_stack')
        product.features = request.form.get('features')
        product.sla = request.form.get('sla')

        if 'product_image' in request.files:
            file = request.files['product_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image = filename

        db.session.commit()
        flash("Solution specifications updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product)


@app.route('/admin/delete/<int:id>')
def delete_product(id):
    if not session.get('user'):
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product removed from catalog.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_inquiry/<int:id>')
def delete_inquiry(id):
    if not session.get('user'):
        return redirect(url_for('login'))
    
    inq = Inquiry.query.get_or_404(id)
    db.session.delete(inq)
    db.session.commit()
    flash("Client inquiry archived.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', 'N/A')
        sender_email = request.form.get('email', 'N/A')
        company = request.form.get('company', 'N/A')
        target_product = request.form.get('product', 'General Corporate')
        timeline = request.form.get('timeline', 'N/A')
        summary = request.form.get('summary', 'No summary provided.')

        # 1. Save Inquiry to Database so you can view it in Admin Panel
        new_inquiry = Inquiry(name=name, email=sender_email, company=company, product=target_product, summary=summary)
        db.session.add(new_inquiry)
        db.session.commit()

        # 2. Send Email via Gmail SMTP
        msg = Message(
            subject=f"[Corporate Inquiry] {company} - {name} ({target_product})",
            recipients=[RECIPIENT_EMAIL],
            reply_to=sender_email,
            body=f"""
NEW CORPORATE INQUIRY TRANSMITTED:

Client Information:
-------------------
Full Name: {name}
Corporate Email: {sender_email}
Company: {company}

Project Scope:
--------------
Target Solution: {target_product}

Executive Summary:
------------------
{summary}
            """
        )
        try:
            mail.send(msg)
            flash("Your message has been transmitted successfully to leadership.", "success")
        except Exception as e:
            flash(f"Email dispatch note: Saved to database successfully (SMTP warning: {str(e)})", "warning")

        return redirect(url_for('contact'))

    corporate_offices = [
        {
            "region": "Global Headquarters",
            "city": "Kampala, Uganda",
            "address": "Horus Tech Plaza, Innovation District",
            "email": "jetdonleeisco5@gmail.com",
            "phone": "+256 700 000 000",
            "hours": "24/7 Operations Center"
        }
    ]
    return render_template('contact.html', offices=corporate_offices)


if __name__ == '__main__':
    app.run(debug=True)