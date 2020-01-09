from flask_login import current_user

def check_for_duplicates(new_city, table):
    records = table.query.all()
    for card in records:
        if (card.city.lower() == new_city.city.lower()) and (current_user.id == card.user_id):
            return True
            break

def check_for_the_same_parameters(new_city, table):
    records = table.query.all()
    for card in records:
        if (card.link == new_city.link) and (card.city.lower() == new_city.city.lower()) and (current_user.id == card.user_id):
            return True
            break

def is_int(var):
    try:
        int(var)
        return True
    except ValueError:
        return False
