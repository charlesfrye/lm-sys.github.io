import subprocess

import modal

app = modal.App("lmsysorg")

image = (
    modal.Image.from_registry("node:20-slim", add_python="3.11")
    .add_local_file("package.json", "/app/package.json", copy=True)
    .add_local_file("package-lock.json", "/app/package-lock.json", copy=True)
    .workdir("/app")
    .run_commands(
        "apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*",
        "npm ci",
    )
    .add_local_dir(".", "/app", copy=True, ignore=["node_modules", ".next", "out", "build"])
    .run_commands(
        "npm run build",
    )
)


@app.function(image=image)
@modal.concurrent(max_inputs=100)
@modal.web_server(3000)
def serve():
    subprocess.Popen(["npx", "next", "start", "--port", "3000"])
