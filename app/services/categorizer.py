# Transaction auto-categorizer
# Will be expanded in Day 2

CATEGORY_KEYWORDS = {
    "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "mcdonald", "subway", "pizza"],
    "Transport": ["uber", "ola", "rapido", "petrol", "fuel", "metro", "irctc"],
    "Shopping": ["amazon", "flipkart", "myntra", "meesho", "mall", "shop"],
    "Utilities": ["electricity", "water", "gas", "broadband", "wifi", "airtel", "jio"],
    "Entertainment": ["netflix", "spotify", "youtube", "prime", "hotstar", "cinema"],
    "Health": ["pharmacy", "hospital", "clinic", "medplus", "apollo", "doctor"],
    "Rent": ["rent", "maintenance", "society"],
    "Salary": ["salary", "payroll", "credit"],
}

def categorize_transaction(description: str) -> str:
    """Categorize a transaction based on its description"""
    description_lower = description.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    
    return "Others"