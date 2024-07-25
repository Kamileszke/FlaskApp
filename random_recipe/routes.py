from flask import render_template, request, flash, redirect, url_for
from .models import User, Recipe
from flask_login import login_user, logout_user, login_required, current_user
import numpy as numpy
import os
import uuid
def register_blueprint(app, db, bcrypt):

    @app.route("/")
    def base():
        user = current_user
        return render_template("base.html", user=user)

    @app.route("/register", methods=['POST', 'GET'])
    def register():
        if current_user.is_authenticated:
            flash(message="YOU ARE ALREADY LOGGED IN", category='error')
            return redirect(url_for('base'))

        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        username = request.form.get('username')

        if request.method=="POST":
            if not User.query.filter(User.email == email).first():
                if not User.query.filter(User.username == username).first():
                    if password==password2:
                        if len(email) > 4:
                            if len(username) > 1:
                                if len(password) > 6:
                                    user = User(email=email.lower(), password=password, username=username)
                                    db.session.add(user)
                                    db.session.commit()
                                    flash("USER HAS BEEN ADDED SUCCESSFULLY", category='success')
                                    return render_template("login.html")
                                else:
                                    flash("PASSWORD MUST BE LONGER THAN 6 CHARACTERS", category='error')
                            else:
                                flash("USERNAME IS EMPTY", category='error')
                        else:
                            flash("EMAIL IS TOO SHORT", category='error')
                    else:
                        flash("PASSWORDS DON'T MATCH", category="error")
                else:
                    flash("THIS USERNAME ALREADY EXISTS!" ,category='error')
            else:
                flash("THIS EMAIL ADDRESS ALREADY EXISTS!", category='error')
        return render_template("register.html")

    @app.route("/login", methods=['POST', 'GET'])
    def login():
        if current_user.is_authenticated:
            flash( message="YOU ARE ALREADY LOGGED IN", category='error')
            return redirect(url_for('base'))

        if request.method=="POST":
            email = request.form.get("email").lower()
            password = request.form.get("password")
            username = request.form.get('username')
            user = User.query.filter_by(email=email).first()
            if user:
                if username.lower() == user.username.lower():
                    if user.password == password:
                        login_user(user)
                        flash("USER LOGGED IN SUCCESSFULLY", category="success")
                        return redirect(url_for('base'))
                    else:
                        flash("WRONG PASSWORD", category="error")
                else:
                    flash("WRONG USERNAME" ,category='error')
            else:
                flash("USER WITH THIS EMAIL DOESN'T EXIST", category="error")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash(message='USER HAS BEEN LOGGED OUT SUCCESSFULLY', category='success')
        return redirect(url_for("login"))

    @app.route("/add_recipe", methods=['POST', 'GET'])
    @login_required
    def add_recipe():
        if request.method=='POST':
            name = request.form.get("name")
            description = request.form.get("description")
            file = request.files.get("image")
            user_id = current_user.id

            if len(name) < 1:
                flash("ENTER A NAME FOR RECIPE", category='error')
                return (render_template("add_recipe.html"))

            elif description == name:
                flash(message="DESCRIPTION AND NAME CAN'T BE THIS SAME",category='error')
                return (render_template("add_recipe.html"))
            elif len(description) < 1:
                flash("ENTER A DESCRIPTION", category='error')
                return (render_template("add_recipe.html"))

            elif not file:
                flash("INSERT AN IMAGE FOR RECIPE", category='error')
                return (render_template("add_recipe.html"))

            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename =f"{uuid.uuid4().hex}-{file.filename}"
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
            file.save(full_path)

            recipe = Recipe(name=name, description=description, path=full_path, user_id=user_id)
            db.session.add(recipe)
            db.session.commit()
            flash('RECIPE HAS BEEN ADDED TO DATABASE SUCCESSFULLY', category='success')
        return (render_template("add_recipe.html"))

    @app.route("/manage_recipe")
    @login_required
    def manage_recipe():
        user = current_user
        if user.email == "admin@gmail.com":
            recipes = Recipe.query.all()
            return render_template("manage_recipe.html", recipes=recipes, user=user)
        recipes = Recipe.query.filter(Recipe.user_id == user.id).all()
        return render_template("manage_recipe.html", recipes=recipes, user=user)

    @app.route("/manage_users")
    @login_required
    def manage_users():
        user = current_user
        users = [user for user in User.query.all() if user.email != 'admin@gmail.com']
        if user.email == "admin@gmail.com":
            return render_template('manage_users.html', users=users)
        else:
            flash("YOU HAVE TO BE LOGGED IN AS ADMIN TO ACCESS THIS PAGE", category="error")
            return redirect(url_for("base"))

    @app.route("/draw_recipe", methods=['POST', 'GET'])
    @login_required
    def draw_recipe():
        if request.method=="POST":
            user = current_user
            if user.email == "admin@gmail.com":
                recipes = Recipe.query.all()
                ids = [recipe.id for recipe in recipes]
                random_id = numpy.random.choice(ids, size=1)

                return (render_template("draw_recipe.html", id=random_id, recipes=recipes))
            recipes = Recipe.query.filter(Recipe.user_id == user.id).all()
            if recipes:
                ids = [recipe.id for recipe in recipes]
                random_id = numpy.random.choice(ids, size=1)

                return (render_template("draw_recipe.html", id=random_id, recipes=recipes))
            else:
                flash("THERE AREN'T ANY RECIPES IN DATABASE", category='error')
                return (redirect(url_for("add_recipe")))
        else:
            return render_template('draw_recipe.html')

    @app.route("/delete/<id>")
    @login_required
    def delete(id):
        recipe = Recipe.query.get(id)
        db.session.delete(recipe)
        db.session.commit()
        os.remove(recipe.path)
        flash("RECIPE HAS BEEN DELETED", category='success')
        return (redirect(url_for("manage_recipe")))

    @app.route("/delete_user/<id>")
    @login_required
    def delete_user(id):
        user = User.query.get(id)
        recipes = Recipe.query.filter(Recipe.user_id==user.id).all()
        for recipe in recipes:
            db.session.delete(recipe)
        db.session.delete(user)
        db.session.commit()
        flash("USER HAS BEEN DELETED", category='success')
        return redirect(url_for("manage_users"))

    @app.route('/test')
    def test():
        recipes = Recipe.query.all()
        ids = [recipe.id for recipe in recipes]
        print(ids)

        return render_template('test.html')




