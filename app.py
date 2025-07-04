import os
from flask import Flask, render_template, request, redirect, url_for, flash
from main import Wallet

# Initialize the Flask application
app = Flask(__name__)
# A secret key is needed for flashing messages to the user
app.secret_key = os.urandom(24)

DATA_FILE = 'data/cards.json'

def _process_form_data(form) -> dict:
    """Helper function to parse form data into the card data dictionary."""
    multipliers = {}
    i = 0
    while f'category-{i}' in form:
        category_name = form[f'category-{i}'].strip().lower().replace(' ', '_')
        multiplier_val = form[f'multiplier-{i}']
        if category_name and multiplier_val:
            try:
                multipliers[category_name] = float(multiplier_val)
            except (ValueError, TypeError):
                # Silently ignore invalid/empty multiplier entries
                pass
        i += 1

    return {
        "card_name": form['card_name'],
        "point_value": float(form['point_value']),
        "default_multiplier": float(form['default_multiplier']),
        "multipliers": multipliers
    }

@app.route('/')
def index():
    """Renders the main page with all card data and analysis."""
    optimizer = Wallet(DATA_FILE)
    all_cards = optimizer.cards
    best_cards_by_category = optimizer.get_best_cards_for_all_categories()
    return render_template(
        'index.html',
        cards=all_cards,
        best_cards=best_cards_by_category,
        messages=None # Compatibility for flashed messages
    )

@app.route('/card/new', methods=['GET', 'POST'])
def add_card():
    """Handles adding a new card."""
    optimizer = Wallet(DATA_FILE)
    if request.method == 'POST':
        try:
            card_data = _process_form_data(request.form)
            optimizer.add_card(card_data)
            flash(f"Card '{card_data['card_name']}' added successfully!", 'success')
        except ValueError as e:
            flash(str(e), 'error')
        return redirect(url_for('index'))

    # For a GET request, show the form
    all_categories = optimizer.get_all_categories()
    return render_template('card_form.html', card=None, all_categories=sorted(list(all_categories)), title="Add New Card", form_action=url_for('add_card'))

@app.route('/card/edit/<path:card_name>', methods=['GET', 'POST'])
def edit_card(card_name):
    """Handles editing an existing card."""
    optimizer = Wallet(DATA_FILE)
    card_to_edit = optimizer.get_card_by_name(card_name)
    if not card_to_edit:
        flash(f"Card '{card_name}' not found.", 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            card_data = _process_form_data(request.form)
            optimizer.update_card(card_name, card_data)
            flash(f"Card '{card_data['card_name']}' updated successfully!", 'success')
        except ValueError as e:
            flash(str(e), 'error')
        return redirect(url_for('index'))

    # For a GET request, show the form populated with card data
    all_categories = optimizer.get_all_categories()
    return render_template('card_form.html', card=card_to_edit, all_categories=sorted(list(all_categories)), title=f"Edit {card_name}", form_action=url_for('edit_card', card_name=card_name))

@app.route('/card/delete/<path:card_name>', methods=['POST'])
def delete_card(card_name):
    """Handles deleting a card."""
    try:
        optimizer = Wallet(DATA_FILE)
        optimizer.delete_card(card_name)
        flash(f"Card '{card_name}' deleted successfully!", 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
