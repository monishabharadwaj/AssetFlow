from __future__ import annotations

# Fixed demo asset tags referenced in DEMO.md and walkthroughs.
DEMO_ASSET_TAGS = {
    "laptop": "IT-LAP-0001",
    "vehicle": "OPS-VAN-001",
    "server": "SRV-PROD-01",
    "printer": "ADM-PRT-001",
}

DEPARTMENTS = [
    ("IT", "Information Technology", "Servers, networking, and end-user devices"),
    ("ENG", "Engineering", "Product engineering and development"),
    ("RND", "Research and Development", "Research labs and prototypes"),
    ("OPS", "Operations", "Fleet and field operations"),
    ("LOG", "Logistics", "Warehouse and distribution"),
    ("HR", "Human Resources", "People operations"),
    ("FIN", "Finance", "Finance and accounting"),
    ("SAL", "Sales", "Revenue and customer teams"),
    ("ADM", "Administration", "General administration"),
    ("FAC", "Facilities", "Building and workplace services"),
]

# category_name -> additional types beyond migration defaults
EXTRA_ASSET_TYPES: dict[str, list[tuple[str, str]]] = {
    "IT Equipment": [
        ("Desktop Workstation", "Fixed desktop computers"),
        ("Monitor", "External displays"),
    ],
    "Office Equipment": [
        ("Conference AV", "Projectors, speakers, and meeting room equipment"),
        ("UPS", "Uninterruptible power supplies"),
    ],
    "Vehicles": [
        ("Delivery Van", "Light commercial delivery vehicles"),
    ],
}

FIRST_NAMES = [
    "Aisha", "Ben", "Carlos", "Diana", "Ethan", "Fatima", "George", "Hannah",
    "Ivan", "Julia", "Kevin", "Lena", "Marcus", "Nina", "Omar", "Priya",
    "Quinn", "Ravi", "Sofia", "Thomas", "Uma", "Victor", "Wendy", "Xavier",
    "Yuki", "Zara", "Alex", "Brooke", "Chen", "Deepa",
]

LAST_NAMES = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Foster", "Garcia", "Hughes",
    "Iyer", "Johnson", "Khan", "Lee", "Martinez", "Nguyen", "Okafor", "Patel",
    "Quinn", "Roberts", "Singh", "Taylor", "Upton", "Vargas", "Williams", "Yamamoto",
]

DEPT_EMPLOYEE_WEIGHTS: dict[str, float] = {
    "ENG": 0.18,
    "IT": 0.12,
    "RND": 0.10,
    "SAL": 0.14,
    "OPS": 0.10,
    "LOG": 0.08,
    "HR": 0.08,
    "FIN": 0.08,
    "ADM": 0.06,
    "FAC": 0.06,
}

# type_name -> (count_weight, assignable_to_employee, default_location_prefix)
ASSET_TYPE_SPECS: dict[str, tuple[float, bool, str]] = {
    "Laptop": (0.28, True, "Floor"),
    "Desktop Workstation": (0.12, True, "Floor"),
    "Server": (0.08, False, "HQ Data Center"),
    "Networking Device": (0.06, False, "Network Closet"),
    "Monitor": (0.04, False, "Floor"),
    "Printer": (0.09, False, "Print Station"),
    "Office Furniture": (0.07, False, "Office"),
    "Conference AV": (0.06, False, "Conference Room"),
    "UPS": (0.05, False, "Server Room"),
    "Company Vehicle": (0.05, True, "Fleet Yard"),
    "Delivery Van": (0.04, True, "Fleet Yard"),
    "Production Machine": (0.06, False, "Production Floor"),
}

DEPT_ASSET_WEIGHTS: dict[str, float] = {
    "IT": 0.22,
    "ENG": 0.20,
    "RND": 0.12,
    "OPS": 0.14,
    "LOG": 0.10,
    "SAL": 0.08,
    "ADM": 0.06,
    "FAC": 0.04,
    "HR": 0.02,
    "FIN": 0.02,
}

MANUFACTURERS = {
    "Laptop": ["Dell", "Lenovo", "HP", "Apple"],
    "Desktop Workstation": ["Dell", "HP", "Lenovo"],
    "Server": ["Dell", "HPE", "Supermicro"],
    "Networking Device": ["Cisco", "Juniper", "Aruba"],
    "Monitor": ["Dell", "LG", "Samsung"],
    "Printer": ["HP", "Canon", "Xerox"],
    "Company Vehicle": ["Toyota", "Ford", "Hyundai"],
    "Delivery Van": ["Mercedes", "Ford", "Ram"],
    "Production Machine": ["Siemens", "ABB", "Fanuc"],
}
