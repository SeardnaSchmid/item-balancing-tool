# Item Balancing Tool

This Streamlit app visualizes and balances items using Success Rate, Efficiency, and Resource distribution. You can add, edit, and visualize items, with costs calculated live based on your balancing rules.

## Features
- Add/edit/remove items with categories, success rates, and efficiency metrics
- Interactive data visualization with scatter plots, bar charts, and more
- Category-based filtering affecting all visualizations
- Resource distribution tracking and cost breakdown
- Balance analysis with recommendations
- Export/import item data as JSON
- **Auto-save functionality** - Data is automatically persisted when changes are made
- **Docker-friendly data persistence** - Works seamlessly in containerized environments

## Data Persistence

The application automatically saves your data when you make changes. It uses a smart fallback system:

1. **Primary**: `/app/data/data.json` (in Docker containers)
2. **Fallback**: `/tmp/item_balancing_data.json` (if primary fails)  
3. **Last resort**: Session-based memory storage

Your data will be preserved between application restarts and Docker container restarts (when using volumes).

## Getting Started

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

### Docker (Recommended for Production)

1. **Quick Start with Docker Compose:**
   ```bash
   # Set up data directory (optional, for persistence across container restarts)
   ./setup_data_dir.sh
   
   # Build and run
   docker-compose up --build
   ```

2. **Manual Docker Setup:**
   ```bash
   # Build the image
   docker build -t item-balancing-tool .
   
   # Run with data persistence
   docker run -p 8502:8501 -v $(pwd)/data:/app/data item-balancing-tool
   ```

The application will be available at `http://localhost:8502`

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
