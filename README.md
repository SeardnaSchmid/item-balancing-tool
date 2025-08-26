# Item Balancing Tool

This Streamlit app visualizes and balances items using Success Rate, Efficiency, and Resource distribution. You can add, edit, and visualize items, with costs calculated live based on your balancing rules.

## Features
- Add/edit/remove items with categories, success rates, and efficiency metrics
- Interactive data visualization with scatter plots, bar charts, and more
- Category-based filtering affecting all visualizations
- Resource distribution tracking and cost breakdown
- Balance analysis with recommendations
- Export/import item data as JSON

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment Options

### Option 1: Streamlit Cloud (Easiest for Sharing)

1. Create a GitHub repository and push your code:

```bash
cd item-balancing-tool
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/item-balancing-tool.git
git push -u origin main
```

2. Visit [Streamlit Cloud](https://share.streamlit.io/) and sign in with your GitHub account
3. Deploy your app by connecting to your repository
4. Share the provided URL with your friend

### Option 2: Standalone Executable (Windows/Mac/Linux)

You can create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "data.json:." app.py
```

The executable will be created in the `dist` folder. You'll need to share both the executable and the data.json file.

### Option 3: Docker Container

1. Create a Dockerfile:

```
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

2. Build and run the container:

```bash
docker build -t item-balancing-tool .
docker run -p 8501:8501 item-balancing-tool
```

## Requirements
- Python 3.8+
- Streamlit
- Plotly
- Pandas

## Customization
You can adjust the cost calculation logic and resource types in `app.py` to fit your game's balancing rules.
