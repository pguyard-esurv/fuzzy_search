# **🔍 Fuzzy Search with Preprocessing**
This repository provides a **fuzzy search implementation** in Python using `rapidfuzz`, enabling **approximate string matching** with **preprocessing rules**.

## **🚀 Features**
✅ **Preprocessing**:
- Expands **common abbreviations** (`Dr.` → `Doctor`).
- Removes **unwanted patterns** (e.g., `"Example 1"` and `"Example 2"` are ignored in the match).
- Converts text to **lowercase** for consistent matching.

✅ **Fuzzy Matching**:
- Uses **`rapidfuzz`** for fast, efficient similarity calculations.
- Supports **two different matching methods** (`ratio` vs `partial_ratio`).

✅ **Customisable Filters**:
- **`ABBREVIATIONS`**: Define abbreviation expansions.
- **`IGNORE_SIMILAR`**: Exclude unwanted phrase matches.

---

## **📥 Installation**
Requires **Python 3.8+** and `rapidfuzz`:
```sh
pip install rapidfuzz
```

Clone this repository:
```sh
git clone https://github.com/yourusername/fuzzy-search.git
cd fuzzy-search
```

---

## **🛠 Usage**
Run the script with:
```sh
python fuzzy_search.py
```

To use **fuzzy search** in your own projects:
```python
from fuzzy_search import fuzzy_search

phrases = [
    "Dr. Smith is a cardiologist",
    "Doctor Smith is a specialist",
    "Example 1",
    "Example 2",
    "This is an example"
]

query = "Example 1"
matches = fuzzy_search(query, phrases, threshold=80, use_partial_ratio=True)

print(matches)  # [('This is an example', 100)]
```

---

## **⚙️ Configuring `ABBREVIATIONS` and `IGNORE_COMBINATIONS`**
### **1️⃣ `ABBREVIATIONS` (Expanding Shortened Words)**
Define **common abbreviations** to be expanded **before matching**:
```python
ABBREVIATIONS = {
    "Dr.": "Doctor",
    "e.g.": "for example",
    "etc.": "et cetera",
}
```
✅ **Example Usage:**
```python
expand_abbreviations("Dr. Smith")  # "Doctor Smith"
expand_abbreviations("e.g. bananas")  # "for example bananas"
```

---

### **2️⃣ `IGNORE_COMBINATIONS` (Excluding Specific Matches)**
In some cases, fuzzy search may return matches that **should be ignored**. Use `IGNORE_COMBINATIONS` to **define specific phrase pairs** that should **never be considered matches**.

```python
IGNORE_COMBINATIONS = [
    (r"example \d+", r"example \d+"),  # Ignore matches between "Example 1" and "Example 2"
    (r"test case \d+", r"test case \d+"),  # Ignore "Test Case 1" matching "Test Case 2"
]
```


### **🔍 Example Behavior**
| Query       | Phrase         | Match Score | **Included in Results?** |
|-------------|---------------|-------------|----------------------|
| `"Example 1"` | `"Example 2"` | **90** | ❌ (Ignored) |
| `"Example 1"` | `"This is an example"` | **100** | ✅ (Included) |
| `"Test Case 1"` | `"Test Case 2"` | **95** | ❌ (Ignored) |

🔹 This ensures that **unwanted duplicate matches** are **automatically removed**.

---

## **📏 Understanding `ratio()` vs `partial_ratio()`**
### **🔹 `fuzz.ratio()` (Default)**
- **Compares full strings**.
- More strict: Needs a **high degree of similarity** to match.
- **Best for:** Comparing entire phrases with **similar length**.

✅ **Example:**
```python
from rapidfuzz import fuzz
fuzz.ratio("example", "this is an example")  # 🔴 Low score (not a full match)
```

---

### **🔹 `fuzz.partial_ratio()`**
- **Compares substrings**, allowing **partial matches**.
- More flexible for **shorter queries** inside longer phrases.
- **Best for:** When **one string is contained in another**.

✅ **Example:**
```python
fuzz.partial_ratio("example", "this is an example")  # ✅ Higher score (substring match)
```

✅ **Comparison Table**
| Query | Phrase | `fuzz.ratio()` | `fuzz.partial_ratio()` |
|--------|--------|-------------|------------------|
| `"example"` | `"example"` | 100 | 100 |
| `"example"` | `"this is an example"` | 50 | 90 |
| `"Dr. Smith"` | `"Doctor Smith is a specialist"` | 80 | 100 |

---

## **🛠 Running Tests**
To run the test suite:
```sh
pytest tests/
```

---

## **📌 Example Output**
```sh
🔍 Query: 'Dr. Smith' (Threshold: 80, Partial: False)
 ✅ Match: 'Doctor Smith is a specialist' (Score: 100)
 ✅ Match: 'Dr. Smith is a cardiologist' (Score: 100)

🔍 Query: 'Example 1' (Threshold: 80, Partial: True)
 ✅ Match: 'This is an example' (Score: 100)

🔍 Query: '' (Threshold: 80, Partial: False)
 ❌ No matches found.
```