from decimal import Decimal


def calculate_prices(city_name, report_drink, drink, club_coordinator, employee_coordinator):
    """Высчитывает цены которые проставляются в ведомости в зависимости от города"""
    if city_name == 'Москва':
        # формула для Москвы
        price_for_club = report_drink.count * drink.price_in_bar * Decimal(0.2)
        price_for_coordinator = report_drink.count * drink.price_in_bar * Decimal(0.05) if employee_coordinator else 0
    else:
        # формула для Питера
        price_for_club = (drink.price_for_sale - drink.price_in_bar) / Decimal(2) * report_drink.count
        if employee_coordinator:
            factor = Decimal(0.5) if club_coordinator == employee_coordinator else Decimal(0.25)
            price_for_coordinator = price_for_club * factor
        else:
            price_for_coordinator = 0
    return price_for_club, price_for_coordinator
