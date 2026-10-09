from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# In-memory database array for inventory items
inventory_db = [
    {
        "id": 1,
        "name": "Nutella Hazelnut Spread",
        "barcode": "3017620422003",
        "category": "Pantry",
        "quantity": 15,
        "price": 4.99
    }
]

# -------------------------------------------------------------------
# External API Integration
# -------------------------------------------------------------------

def fetch_openfoodfacts_product(barcode):
    """Fetch product details from OpenFoodFacts API using barcode."""
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    headers = {"User-Agent": "InventoryManagementApp/1.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                return {
                    "name": product.get("product_name", "Unknown Product"),
                    "category": product.get("categories", "General").split(",")[0],
                    "barcode": barcode
                }
    except requests.RequestException:
        return None
    return None

# -------------------------------------------------------------------
# REST API CRUD Routes
# -------------------------------------------------------------------

# READ ALL (GET)
@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    return jsonify({"success": True, "data": inventory_db, "count": len(inventory_db)}), 200

# READ ONE (GET)
@app.route("/api/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((i for i in inventory_db if i["id"] == item_id), None)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404
    return jsonify({"success": True, "data": item}), 200

# CREATE (POST)
@app.route("/api/inventory", methods=["POST"])
def create_item():
    data = request.get_json() or {}
    if not data.get("name") or "quantity" not in data or "price" not in data:
        return jsonify({"success": False, "error": "Missing required fields: name, quantity, price"}), 400

    new_id = max([i["id"] for i in inventory_db], default=0) + 1
    new_item = {
        "id": new_id,
        "name": data["name"],
        "barcode": data.get("barcode", ""),
        "category": data.get("category", "General"),
        "quantity": int(data["quantity"]),
        "price": float(data["price"])
    }
    inventory_db.append(new_item)
    return jsonify({"success": True, "data": new_item}), 201

# UPDATE / PATCH (PATCH)
@app.route("/api/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = next((i for i in inventory_db if i["id"] == item_id), None)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404

    data = request.get_json() or {}
    if "name" in data: item["name"] = data["name"]
    if "category" in data: item["category"] = data["category"]
    if "quantity" in data: item["quantity"] = int(data["quantity"])
    if "price" in data: item["price"] = float(data["price"])
    if "barcode" in data: item["barcode"] = data["barcode"]

    return jsonify({"success": True, "data": item}), 200

# DELETE (DELETE)
@app.route("/api/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global inventory_db
    item = next((i for i in inventory_db if i["id"] == item_id), None)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404

    inventory_db = [i for i in inventory_db if i["id"] != item_id]
    return jsonify({"success": True, "message": f"Item {item_id} deleted successfully"}), 200

# -------------------------------------------------------------------
# Helper Routes & External API Integration Endpoint
# -------------------------------------------------------------------

# HELPER ROUTE: Search by name or category
@app.route("/api/inventory/search", methods=["GET"])
def search_inventory():
    query = request.args.get("q", "").lower()
    results = [
        i for i in inventory_db 
        if query in i["name"].lower() or query in i["category"].lower()
    ]
    return jsonify({"success": True, "data": results, "count": len(results)}), 200

# EXTERNAL API INTEGRATION ROUTE: Fetch product info & auto-add to DB array
@app.route("/api/inventory/fetch-external/<string:barcode>", methods=["POST"])
def fetch_and_add_external(barcode):
    product_info = fetch_openfoodfacts_product(barcode)
    if not product_info:
        return jsonify({"success": False, "error": "Product not found on OpenFoodFacts API"}), 404

    payload = request.get_json() or {}
    new_id = max([i["id"] for i in inventory_db], default=0) + 1
    new_item = {
        "id": new_id,
        "name": product_info["name"],
        "barcode": barcode,
        "category": product_info["category"],
        "quantity": int(payload.get("quantity", 1)),
        "price": float(payload.get("price", 0.0))
    }
    inventory_db.append(new_item)
    return jsonify({"success": True, "message": "Product imported successfully", "data": new_item}), 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)
