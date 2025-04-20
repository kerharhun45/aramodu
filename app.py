from flask import Flask, render_template, abort, request, redirect, url_for, flash, session
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "dev" #cmle5fvuzn4398ohncvrhlkujwezjfiuwezjfiozsdehfrjklidusjhtjcejdhgwkdjfjhfjcvfkzchslcmkjfnhskaejmgukvmjnfhijuclsdklkmcvjdvgkcjmlr"



def find_all():
    with open('recipes.txt', encoding='utf-8') as file:
        recipes = []

        file.readline()  # header

        for line in file:
            values = line.strip().split(';')

            recipe = {
                'id': int(values[0]),
                'ar': int(values[1]),
                'merte': values[2],
                'nev': values[3],
                'leiras': values[4],
                'kep': values[5]

            }


            recipes.append(recipe)

        return recipes

def security():
    with open("users.json") as file:
        users = json.load(file)
    try:
        username = session['username']
        if users[username]['admine'] == "true":
            return True
        else:
            return False
    except:
        print('nincs username')

def next_order_id():
    with open("orders.txt","r") as file:

        orders = []
        file.readline()
        for line in file:
            if line != "":
                values = line.strip().split(';')
                order = {
                    'id': values[0],
                    'username': values[1],
                    'products': values[2]
                }
                orders.append(order)
        print(orders[-1]['id'])
        return str(int(orders[-1]['id'])+1)


@app.route("/profile")
def profile():

    if security():
        admine = "van"
    else:
        admine = "nincs"

    try:
        session['username']
    except:
        flash('Jelentkezz előbb be!')
        return redirect(url_for('login'))
    return render_template('profile.html', fnev=session['username'], admine=admine)

@app.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        with open("users.json") as file:
            users = json.load(file)

        username = request.form['felhasznalonev'].lower()
        password = request.form['jelszo']

        if username in users and password == users[username]['jelszo']:
            session['username'] = username
            flash('Bejelentkezés sikeres.')
            return redirect(url_for('list_all'))
        flash("Bejelentkezés sikertelen.")
        return render_template('login.html')

    if request.method == 'GET':
        return render_template('login.html')

"""
        password = "supersecretpassword"
hashed_password = generate_password_hash(password)

print(f"Hashelt jelszó: {hashed_password}")

# Jelszó ellenőrzése (például bejelentkezéskor)
entered_password = "supersecretpassword"
if check_password_hash(hashed_password, entered_password):
    print("A jelszó helyes!")
else:
    print("Hibás jelszó.")
"""

@app.route('/cart', methods=('POST','GET'))
def cart(products=None):
    if request.method == 'GET':
        recipes = find_all()
        products = []
        try:
            for i in range(len(recipes)):
                if i in session['cart']:
                    products.append(find_by_id(i))
        except:
            pass


        return render_template('cart.html', recipes=products)
    if request.method == 'POST':
        if request.form['add'] > "-1":
            if 'cart' not in session:
                session['cart'] = []
            cart = session['cart']
            if int(request.form['add']) not in cart:
                cart.append(int(request.form['add']))
                #flash("Kosárban!") felesleges, nincs újratöltés
            session['cart'] = cart

        if request.form['delete'] == "-1": #minden törlése
            cart = []
            session['cart'] = cart
            return redirect(url_for('cart'))

        elif request.form['delete'] == "-2" and session['cart']: #megrendelés
            try:
                session['username']
            except:
                flash("Előbb jelentkezz be!")
                return redirect(url_for('login'))
            try:
                nextId = next_order_id()
            except:
                nextId = "0"

            with open("orders.txt","a") as file:
                darab = ""
                for i in range(len(session['cart'])):
                    if darab == "":
                        darab = str(session['cart'][i])
                    else:
                        darab = darab+","+str(session['cart'][i])
                sor = "\n"+str(nextId)+";"+session['username']+";"+darab
                file.write(sor)
            session['cart'] = []
            flash("Megrendelve!")
            return redirect(url_for('cart'))

        else:
            cart = session['cart']
            new_cart = []
            for i in range(len(cart)):
                if cart[i] != int(request.form['delete']):
                    new_cart.append(cart[i])
            session['cart'] = new_cart
            return redirect(url_for('cart'))


@app.route('/create', methods=('POST', 'GET'))
def create():
    if security():
        if request.method == 'POST':
            with open('recipes.txt', encoding='utf-8') as file:
                recipes = []

                file.readline()  # header

                for line in file:
                    values = line.strip().split(';')

                    recipe = {
                        'id': int(values[0]),
                        'ar': int(values[1]),
                        'merte': values[2],
                        'nev': values[3],
                        'leiras': values[4],
                        'kep': values[5]

                    }
                    alma = int(values[0])

                    recipes.append(recipe)

            print('[alma]: ' + str(alma))
            print(request.form)
            #return str(request.form['leiras'])
            if request.form['kep'] == "" or request.form['kep'] == "none":
                RFkep = 'https://modulshop.cdn.shoprenter.hu/custom/modulshop/image/cache/w210h210q100/product/10%20Elektronika/04-ellen%C3%A1l%C3%A1sok%2Cpotik/10-4-40_Cement5w01ohm-1.webp?lastmod=1713781705.1731280985'
            else:
                RFkep = request.form['kep']

            if request.form['merte'] == "":
                RFmerte = "Ft"
            else:
                RFmerte = request.form['merte']

            if request.form['ar'] == "" or request.form['nev'] == "" or request.form['leiras'] == "":
                pass
            else:
                sor = str(alma+1)+";"+request.form['ar']+";"+RFmerte+";"+request.form['nev']+";"+request.form['leiras']+";"+RFkep+"\n"
                print(sor)

                fa = open('recipes.txt', 'a')
                fa.write(sor)
                fa.close()
                flash("Létrehozva!")
                return redirect(url_for('edit'))

        return render_template('create.html')
    # routes
    else:
        return render_template('notallowed.html')

@app.route('/edit')#, methods=('POST', 'GET'))
def edit():
    if security():
        if request.args.get('search'):
            recipes = find_all_by_name_like(request.args.get('search'))
        else:
            with open('recipes.txt', encoding='utf-8') as file:
                recipes = []

                file.readline()  # header

                for line in file:
                    values = line.strip().split(';')

                    recipe = {
                        'id': int(values[0]),
                        'ar': int(values[1]),
                        'merte': values[2],
                        'nev': values[3],
                        'leiras': values[4],
                        'kep': values[5]

                    }
                    recipes.append(recipe)
        return render_template('edit.html', recipes=recipes)
    else:
        return render_template('notallowed.html')

@app.route('/')
def list_all():
    if request.args.get('search'):
        recipes = find_all_by_name_like(request.args.get('search'))
    else:
        recipes = find_all()

    return render_template('list.html', recipes=recipes)

@app.route('/<int:recipe_id>')
def view(recipe_id):
    recipe = find_by_id(recipe_id) or abort(404)

    return render_template('view.html', recipe=recipe)

@app.route('/delete/<int:recipe_id>')
def delete(recipe_id):
    if security():
        recipes = [recipe for recipe in find_all() if recipe['id'] != recipe_id]

        with open('recipes.txt', 'w', encoding='utf-8') as file:
            file.write('id  ar mert.e.  nev	leiras  kep\n')
            for i in range(len(recipes)):
                sor = str(recipes[i]['id'])+";"+str(recipes[i]['ar'])+';'+recipes[i]['merte']+';'+recipes[i]['nev']+';'+recipes[i]['leiras']+';'+recipes[i]['kep']+'\n'
                file.write(str(sor))
        flash("Törölve!")
        return redirect(url_for('edit'))

@app.route('/edit/<int:recipe_id>', methods=('POST', 'GET'))
def editview(recipe_id):
    if security():
        if request.method == 'POST':
            print(request.form)


            recipes = find_all()


            RFnev = request.form['nev'].replace(';', ':')#biztonság, hogy ne essen szét a fájlrendszer ha vki ;-t ír be.
            RFleiras = request.form['leiras'].replace(';', ':')#az ár is csak kliensoldalról korlátozott!!!

            sor = str(recipe_id)+";"+request.form['ar']+";"+request.form['merte']+';'+RFnev+";"+RFleiras+";"+request.form['kep']+"\n"
            print(sor)

            fa = open('recipes.txt', 'w')
            fa.write('id  ar   nev	leiras  kep\n')
            for i in range(0,len(recipes)):
                print(str(i))
                if i != recipe_id:
                    print(recipes[i])
                    line = str(recipes[i]['id'])+";"+str(recipes[i]['ar'])+";"+recipes[i]['merte']+";"+recipes[i]['nev']+";"+recipes[i]['leiras']+";"+recipes[i]['kep']+"\n"
                    print(line)
                    fa.write(line)
                if i == recipe_id:
                    fa.write(sor)

            fa.close()
            flash("Szerkesztve!")
            return redirect(url_for('edit'))

        recipe = find_by_id(recipe_id) or abort(404)

        return render_template('editview.html', recipe=recipe)
    else:
        return render_template('notallowed.html')

def find_by_id(recipe_id):
    for recipe in find_all():
        if recipe['id'] == recipe_id:
            return recipe

    return None

def find_all_by_name_like(name):
    recipes = []

    for recipe in find_all():
        if name.lower() in recipe['nev'].lower():
            recipes.append(recipe)

    return recipes


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
