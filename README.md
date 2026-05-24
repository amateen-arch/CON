# 📝 Text-to-Handwriting Converter

A simple Python application that takes digital text and converts it into realistic, handwritten pages. Perfect for assignments, notes, or creating personalized documents.

---

## ✨ Features
* **Choose Your Tool:** Switch between **Blue Pen** or a thick **Marker** style.
* **Choose Your Page:** Swap between a standard **A4 Plain Paper** or a classic **Lined Register Sheet**.
* **Font Variety:** Select between **2 distinct handwriting fonts** to match your style.
* **Instant PDF Export:** Saves your final generated pages directly as a ready-to-submit **PDF**.

## 📁 Project Structure
* `gui.py` — The control panel. Pick your pen, paper, font, paste your text, and hit export.
* `engine.py` — The magic under the hood. It handles the text wrapping, spacing, and image rendering.
* `assets/` — Stores the high-res paper textures (A4 & Register) and custom handwriting fonts.

---

## 🛠️ How It Works (The Logic)
1. **Input:** You type or paste your text into the GUI and select your styling preferences (Font, Paper Type, Ink Type).
2. **Processing (`engine.py`):** * The script loads the selected paper texture from the `assets/` folder.
   * It calculates margins and line-spacing so the text lines up perfectly with the register lines (if selected).
   * It dynamically wraps your text so it doesn't clip off the edge of the page.
3. **Output:** If the text is long, it automatically splits it across multiple pages and compiles everything into a single, clean **PDF file**.

---

## 🚀 How to Run It

### 1. Install Dependencies
Make sure you have Python installed, then install the required libraries using your terminal:
```bash
pip install -r requirements.txt
