# 📝 Text-to-Handwriting Converter

A simple Python desktop application that takes digital text and converts it into realistic, handwritten pages. Perfect for assignments, notes, or creating personalized documents.

---

## ✨ Features
* **Choose Your Tool:** Switch between **Blue Pen** or a thick **Marker** style.
* **Choose Your Page:** Swap between a standard **A4 Plain Paper** or a classic **Lined Register Sheet**.
* **Font Variety:** Select between **2 distinct handwriting fonts** to match your style.
* **Instant PDF Export:** Saves your final generated pages directly as a ready-to-submit **PDF**.

---

## 🛠️ How It Works (The Logic)
1. **Input:** You type or paste your text into the GUI and select your styling preferences (Font, Paper Type, Ink Type).
2. **Processing (`engine.py`):** * The script loads the selected paper texture from the `assets/` folder.
   * It calculates margins and line-spacing so the text lines up perfectly with the register lines (if selected).
   * It dynamically wraps your text so it doesn't clip off the edge of the page.
3. **Output:** If the text is long, it automatically splits it across multiple pages and compiles everything into a single, clean **PDF file**.

---

## 📁 Project Structure
* `gui.py` — The control panel. Pick your pen, paper, font, paste your text, and hit export.
* `engine.py` — The magic under the hood. It handles the text wrapping, spacing, and image rendering.
* `assets/` — Stores the high-res paper textures (A4 & Register) and custom handwriting fonts.

---

## 🚧 Current Status & Future Roadmap
* **Current Release:** The desktop GUI version is fully stable, complete, and ready to use!
* **Next Up:** I am actively building a **Web Application version** of this tool on a separate development branch so users can use it right from their browsers instead of downloading it.

> 🤝 **Looking for Collaborators!** If you want to help transition this logic to a web app (or just want to talk Python), I'd love to team up. Check out the codebase, DM me on Reddit, or open an issue here!

---

## 🚀 How to Clone and Run It

For new users looking to download, set up, and run this project locally, execute the following commands in your terminal or command prompt:

```bash
# 1. Clone the repository and enter the project folder
git clone "https://github.com/amateen-arch/TextToHandwriting" (without the double comma)
cd YOUR_REPOSITORY_NAME

# 2. Install all required setup dependencies
pip install -r requirements.txt

# 3. Launch the application
python gui.py
