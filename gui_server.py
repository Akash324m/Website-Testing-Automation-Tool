import asyncio
import json
import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Web Automation Tool Controller")

# Global state
active_process: Optional[asyncio.subprocess.Process] = None
log_queue: asyncio.Queue = asyncio.Queue()

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join("static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


async def read_stream(stream, prefix=""):
    """Reads lines from a stream and puts them into the log queue."""
    while True:
        line = await stream.readline()
        if not line:
            break
        decoded_line = line.decode("utf-8", errors="replace").strip()
        if decoded_line:
            print(f"{prefix}{decoded_line}")
            await log_queue.put(json.dumps({"type": "log", "text": decoded_line}))


async def run_subprocess(cmd: list):
    """Runs a subprocess and monitors its output."""
    global active_process, log_queue

    # Clear the queue first
    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

    try:
        active_process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=asyncio.subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        # Read stdout and stderr concurrently
        await asyncio.gather(
            read_stream(active_process.stdout, "[STDOUT] "),
            read_stream(active_process.stderr, "[STDERR] "),
        )

        return_code = await active_process.wait()

        if return_code == 0:
            await log_queue.put(json.dumps({"type": "status", "text": "done"}))
        else:
            await log_queue.put(json.dumps({"type": "status", "text": "error"}))

    except Exception as e:
        await log_queue.put(
            json.dumps({"type": "log", "text": f"Error running process: {e}"})
        )
        await log_queue.put(json.dumps({"type": "status", "text": "error"}))
    finally:
        active_process = None


@app.get("/api/crawl")
async def start_crawl(url: str, depth: int = 1):
    global active_process
    if active_process is not None:
        raise HTTPException(status_code=400, detail="A process is already running")

    cmd = [
        sys.executable,
        "examples/run_real_site.py",
        "crawl",
        url,
        "--depth",
        str(depth),
    ]
    asyncio.create_task(run_subprocess(cmd))
    return {"status": "started"}


@app.get("/api/run")
async def start_run(goal: str, start_url: str):
    global active_process
    if active_process is not None:
        raise HTTPException(status_code=400, detail="A process is already running")

    cmd = [sys.executable, "examples/run_real_site.py", "run", goal, start_url]
    asyncio.create_task(run_subprocess(cmd))
    return {"status": "started"}


@app.post("/api/stop")
async def stop_process():
    global active_process
    if active_process is None:
        return {"status": "no process running"}

    try:
        active_process.terminate()
        await active_process.wait()
        await log_queue.put(
            json.dumps({"type": "log", "text": "Process terminated by user."})
        )
        await log_queue.put(json.dumps({"type": "status", "text": "done"}))
    except Exception as e:
        print(f"Error terminating process: {e}")

    active_process = None
    return {"status": "stopped"}


@app.get("/api/logs")
async def stream_logs():
    async def log_generator():
        while True:
            try:
                item = await log_queue.get()
                yield f"data: {item}\n\n"

                # Check if it was a termination status
                data = json.loads(item)
                if data.get("type") == "status":
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                yield f"data: {json.dumps({'type': 'log', 'text': f'SSE error: {e}'})}\n\n"
                break

    return StreamingResponse(log_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    # Disable reload in production to prevent subprocess cycle issues on save
    uvicorn.run("gui_server:app", host="127.0.0.1", port=8080, reload=False)
