# Guide: How to Use the Web Automation Tool on a New Website

This guide walks you through setting up and running this web automation tool for any website that has not been crawled before.

The architecture uses a two-phase pipeline:
1. **Offline Phase (Crawling & Indexing)**: Maps the target site structures into a graph and embeds page data into a vector index.
2. **Runtime Phase (Execution)**: Evaluates user natural language goals, retrieves target pages, plans navigation paths, and executes browser actions autonomously.

---

## Prerequisites
Ensure you are in the project root directory and the Python virtual environment is activated:

```bash
# On Windows PowerShell
.\.venv\Scripts\Activate.ps1

# On macOS/Linux
source .venv/bin/activate
```

---

## Phase 1: Mapped Site Setup (Offline Crawling)

Before the agent can execute any tasks on a new site, it must map the site. The `Navigator` will explore the site up to a specific depth, building an interaction state graph.

### Run the Crawl Command
Execute the runner script using the `crawl` subcommand:

```bash
python examples/run_real_site.py crawl <START_URL> --depth <MAX_DEPTH>
```

#### Parameters:
- `url`: The homepage or starting page of the target website (must include `http://` or `https://`).
- `--depth`: *(Optional)* How deep the crawler should follow internal link pathways.
  - `--depth 1` (Default): Crawls only the starting page and elements directly on it.
  - `--depth 2` or `3`: Recommended for medium-sized websites with nested navigation menus (e.g. dashboards, login walls, product details).

#### Example:
```bash
python examples/run_real_site.py crawl https://quotes.toscrape.com --depth 2
```

### Verify Crawl Deliverables
Once the crawl completes, verify that a new folder named `crawl_data/` has been created in your project root with the following files:
- **`graph.json`**: The structural site layout mapping pages (nodes) and links (edges).
- **`faiss_index.index` & `faiss_index.json`**: The semantic search index containing vector representations of all crawled states.
- **`cache.json`**: Caches structural DOM hashes to enable **incremental crawling** (ensuring subsequent crawls skip unchanged pages).

---

## Phase 2: Autonomous Goal Execution (Runtime)

Once the files are present inside `crawl_data/`, you can use natural language goals to instruct the automation agent to execute complex navigations.

### Run the Execution Command
Use the `run` subcommand to input a natural language command:

```bash
python examples/run_real_site.py run "<YOUR_GOAL>" <START_URL>
```

#### Parameters:
- `"goal"`: What you want the agent to do (e.g., `"Go to the login page"`, `"Find contact info"`, `"Search for products"`).
- `start_url`: The URL the browser should launch at (must match a page that was crawled in Phase 1).

#### Example:
```bash
python examples/run_real_site.py run "I want to login to my account" https://quotes.toscrape.com
```

---

## Customizing & Troubleshooting

### Handling Dynamic Elements & Session IDs
If your target site loads dynamic elements (such as variable session tokens in URLs, random IDs, or changing advertisements), the cache system's **`DOMHasher`** automatically filters out likely dynamic selectors. This prevents the crawler from incorrectly thinking a page has changed when it has not.

### Changing the Model used for Vector Embeddings
The agent uses `all-MiniLM-L6-v2` by default (384-dimensional vector space). If you want to use a different embedding model, adjust the parameters in `crawler/embeddings/embedder.py`.

### Debugging Failures
- Look at the console logs printed directly by the script.
- If the browser gets stuck or fails to navigate, review the screenshots generated in `crawl_data/` (or the vision fallback modules in `crawler/vision/` if integrated).

---

## Interactive Web GUI Dashboard

If you prefer a visual interface rather than typing raw terminal commands:
1. Start the GUI Web Server:
   ```bash
   python gui_server.py
   ```
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```
3. Use the **Offline Crawling** panel to input a URL and depth, then click **Crawl & Map Website**.
4. Monitor progress directly via the **Live Output & Execution Logs** terminal screen.
5. Use the **Goal Execution Agent** panel to run natural language tasks against your indexed sites.
6. Stop any active tasks instantly by clicking **Terminate Active Task**.

