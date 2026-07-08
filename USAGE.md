# Web Automation Tool Usage Guide

Welcome to the End-to-End Live Web Automation Testing Tool! This guide explains how to use the tool to automate interactions on a new, previously uncrawled website.

The tool operates in two distinct phases:
1. **Offline Crawling Phase**: Maps the website and builds a knowledge database.
2. **Runtime Execution Phase**: Uses natural language goals to navigate the site based on the knowledge database.

---

## 1. Offline Crawling Phase (The "Map")

Before the agent can understand how to navigate a new website, you must let it crawl the site to build a "map" of the available pages, components, and semantic information.

### What happens during this phase?
- The crawler spins up a headless browser.
- It navigates through the target URL up to a specified depth.
- It records the structural layout (DOM elements, buttons, links).
- It generates semantic vector embeddings to understand the purpose of each page and interactive element.
- It saves these artifacts (`graph.json`, `faiss_index.bin`, `cache.json`, etc.) in the `crawl_data/` folder.

### How to run it:
Using the command-line interface (CLI), you can start the crawl phase by running:

```bash
python examples/run_real_site.py crawl <TARGET_URL> --depth <DEPTH>
```
- `<TARGET_URL>`: The starting URL of the website you want to test (e.g., `https://example.com`).
- `--depth`: (Optional) How many levels deep the crawler should go. Default is 1. Be careful with large values as crawling can take time!

**Example:**
```bash
python examples/run_real_site.py crawl https://quotes.toscrape.com/ --depth 2
```

---

## 2. Runtime Execution Phase (The "Agent")

Once the offline phase is successfully completed and the `crawl_data/` folder is populated, you can command the agent using natural language goals.

### What happens during this phase?
- The tool loads the previously generated `graph.json` and vector database (`faiss_index.index`).
- It interprets your natural language goal (e.g., "Click on the login button").
- It spins up a browser, navigates to the starting URL, and plans the shortest sequence of actions to achieve your goal.
- It executes those actions in real-time.

### How to run it:
Use the CLI to start the execution phase:

```bash
python examples/run_real_site.py run "<YOUR_GOAL>" <STARTING_URL>
```
- `<YOUR_GOAL>`: What you want the agent to achieve, described in plain English.
- `<STARTING_URL>`: The URL from which the agent should start its task (usually the same as the target URL from the crawl phase).

**Example:**
```bash
python examples/run_real_site.py run "Go to the login page" https://quotes.toscrape.com/
```

---

## 3. Using the Web GUI

We also provide a simple, user-friendly Web Interface to manage these tasks without touching the command line.

### Starting the GUI
1. Run the GUI server:
   ```bash
   python gui_server.py
   ```
2. Open your web browser and navigate to `http://localhost:8080`.

### Using the GUI
- **Crawl a Website**: Enter the target URL and depth in the respective fields, then click **"Start Crawl"**. The log viewer will show you the real-time progress.
- **Run a Goal**: After crawling, enter your natural language goal and the starting URL, then click **"Run Goal"**.
- **Stop Process**: If a process is taking too long or you made a mistake, you can use the **"Stop Process"** button to terminate it safely.

---

## Troubleshooting

- **`crawl_data` errors during Runtime**: If you see errors saying `graph.json` or `faiss_index.index` are missing, it means the Offline Crawling Phase failed or hasn't been run yet. Always run the `crawl` command first on a new site.
- **Agent gets stuck**: Ensure the depth provided during the crawl phase was sufficient to map the page needed to achieve the goal.
