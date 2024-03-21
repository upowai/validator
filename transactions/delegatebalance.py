from database.database import r
from database.leveldatabase import store_in_db, retrieve_from_db


def update_delegate_balances(amount, sorted_delegates, block_range_str):
    delegate_updates = {}
    try:
        for delegate_info in sorted_delegates[1]:
            delegate = delegate_info["delegate"]
            percentage = delegate_info["percentage"]

            if percentage < 0.00000001:
                print(f"Percentage for delegate {delegate} is too small to process.")
                continue

            amount_to_add = round((amount * percentage) / 100, 8)

            if amount_to_add == 0:
                print(
                    f"Calculated amount for delegate {delegate} is too small to process."
                )
                continue

            if r.hexists("delegates_list", delegate):
                current_balance = float(r.hget("delegates_list", delegate))
                previous_balance = current_balance
                new_balance = round(current_balance + amount_to_add, 8)
            else:
                previous_balance = 0.0
                new_balance = amount_to_add

            r.hset("delegates_list", delegate, new_balance)

            # Update delegate_updates with the necessary information
            delegate_updates[delegate] = {
                "previous_balance": previous_balance,
                "added_amount": amount_to_add,
                "current_balance": new_balance,
            }

        # Store the updates in DB
        store_in_db(f"delegate_{block_range_str}", delegate_updates)
        retrieve_from_db(f"delegate_{block_range_str}")

        print("Delegate balances updated successfully.")
    except Exception as e:
        print(f"update_delegate_balances An error occurred: {e}")
