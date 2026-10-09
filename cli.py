import sys
import requests

API_BASE_URL = "http://127.0.0.1:5000/api/inventory"

def display_menu():
    print("\n" + "="*45)
    print(" INVENTORY MANAGEMENT ADMIN PORTAL ")
    print("="*45)
    print("1. View All Inventory Items")
    print("2. Search Items by Name or Category")
    print("3. Add New Item Manually")
    print("4. Fetch & Add Item via Barcode (External API)")
    print("5. Update Item (Patch)")
    print("6. Delete Item")
    print("7. Exit")
    print("="*45)

def list_items():
    try:
        res = requests.get(API_BASE_URL)
        data = res.json()
        print(f"\n--- Current Inventory ({data['count']} items) ---")
        for item in data['data']:
            print(f"ID: {item['id']} | Name: {item['name']} | Qty: {item['quantity']} | Price: ${item['price']:.2f} | Category: {item['category']} | Barcode: {item['barcode']}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

def search_items():
    query = input("Enter search keyword (name/category): ").strip()
    try:
        res = requests.get(f"{API_BASE_URL}/search?q={query}")
        data = res.json()
        print(f"\n--- Search Results ({data['count']} found) ---")
        for item in data['data']:
            print(f"ID: {item['id']} | {item['name']} | Qty: {item['quantity']} | ${item['price']:.2f}")
    except Exception as e:
        print(f"Error: {e}")

def add_manual_item():
    print("\n--- Add Manual Item ---")
    name = input("Item Name: ").strip()
    category = input("Category: ").strip() or "General"
    barcode = input("Barcode (optional): ").strip()
    try:
        quantity = int(input("Quantity: "))
        price = float(input("Price ($): "))
    except ValueError:
        print("Invalid number input.")
        return

    payload = {"name": name, "category": category, "barcode": barcode, "quantity": quantity, "price": price}
    res = requests.post(API_BASE_URL, json=payload)
    if res.status_code == 201:
        print("✅ Item added successfully!")
    else:
        print(f"❌ Failed: {res.json().get('error')}")

def add_external_item():
    print("\n--- Auto-Add via Barcode (OpenFoodFacts API) ---")
    barcode = input("Enter Barcode (e.g., 3017620422003): ").strip()
    try:
        quantity = int(input("Initial Quantity (default 1): ") or 1)
        price = float(input("Unit Price ($): ") or 0.0)
    except ValueError:
        print("Invalid numeric values.")
        return

    url = f"{API_BASE_URL}/fetch-external/{barcode}"
    res = requests.post(url, json={"quantity": quantity, "price": price})
    
    if res.status_code == 201:
        data = res.json()["data"]
        print(f"✅ Imported: '{data['name']}' (Category: {data['category']}) into inventory!")
    else:
        print(f"❌ Error: {res.json().get('error')}")

def update_item():
    list_items()
    item_id = input("\nEnter Item ID to update: ").strip()
    print("Leave fields blank to keep current value.")
    
    name = input("New Name: ").strip()
    quantity = input("New Quantity: ").strip()
    price = input("New Price ($): ").strip()
    
    payload = {}
    if name: payload["name"] = name
    if quantity: payload["quantity"] = int(quantity)
    if price: payload["price"] = float(price)

    if not payload:
        print("No changes specified.")
        return

    res = requests.patch(f"{API_BASE_URL}/{item_id}", json=payload)
    if res.status_code == 200:
        print("✅ Item updated successfully!")
    else:
        print(f"❌ Update failed: {res.json().get('error')}")

def delete_item():
    list_items()
    item_id = input("\nEnter Item ID to delete: ").strip()
    res = requests.delete(f"{API_BASE_URL}/{item_id}")
    if res.status_code == 200:
        print("✅ Item deleted successfully!")
    else:
        print(f"❌ Delete failed: {res.json().get('error')}")

def main():
    while True:
        display_menu()
        choice = input("Select an option (1-7): ").strip()
        if choice == "1": list_items()
        elif choice == "2": search_items()
        elif choice == "3": add_manual_item()
        elif choice == "4": add_external_item()
        elif choice == "5": update_item()
        elif choice == "6": delete_item()
        elif choice == "7":
            print("Exiting Admin Portal.")
            sys.exit(0)
        else:
            print("Invalid selection. Try again.")

if __name__ == "__main__":
    main()
