from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Date
from datetime import datetime

db = SQLAlchemy()

class Medication(db.Model):
    __tablename__ = 'medications'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    stock = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    expiry_date = Column(Date, nullable=False)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/pharmacy_perplexity_02_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        medications = Medication.query.all()
        return render_template('index.html', medications=medications)

    @app.route('/add', methods=['GET', 'POST'])
    def add_medication():
        if request.method == 'POST':
            name = request.form['name']
            stock = int(request.form['stock'])
            cost = float(request.form['cost'])
            expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()

            new_medication = Medication(name=name, stock=stock, cost=cost, expiry_date=expiry_date)

            try:
                db.session.add(new_medication)
                db.session.commit()
                flash('Medication added successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                return redirect(url_for('add_medication'))

        return render_template('add.html')

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit_medication(id):
        medication = Medication.query.get_or_404(id)

        if request.method == 'POST':
            medication.name = request.form['name']
            medication.stock = int(request.form['stock'])
            medication.cost = float(request.form['cost'])
            medication.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()

            try:
                db.session.commit()
                flash('Medication updated successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
                return redirect(url_for('edit_medication', id=id))

        return render_template('edit.html', medication=medication)

    @app.route('/delete/<int:id>')
    def delete_medication(id):
        medication = Medication.query.get_or_404(id)

        try:
            db.session.delete(medication)
            db.session.commit()
            flash('Medication deleted successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('index'))

    @app.route('/search', methods=['GET', 'POST'])
    def search_medication():
        if request.method == 'POST':
            search_term = request.form['search_term']
            medications = Medication.query.filter(Medication.name.like(f'%{search_term}%')).all()
            return render_template('search.html', medications=medications, search_term=search_term)
        return render_template('search.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
