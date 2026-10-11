
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

TOTAL_MEMORY = 1000
history = []
message = ""
success = True


class MemoryBlock:
    def __init__(self, size, process=None):
        self.size = size
        self.process = process
        self.next = None


class MemoryManager:
    def __init__(self, total_memory):
        self.head = MemoryBlock(total_memory)

    def allocate(self, process, size):
        current = self.head

        while current:
            if current.process is None and current.size >= size:
                remaining = current.size - size

                if remaining > 0:
                    new_block = MemoryBlock(remaining)
                    new_block.next = current.next
                    current.next = new_block

                current.size = size
                current.process = process
                return True, remaining

            current = current.next

        return False, 0

    def deallocate(self, process):
        current = self.head

        while current:
            if current.process == process:
                released = current.size
                current.process = None
                return True, released

            current = current.next

        return False, 0

    def get_blocks(self):
        blocks = []
        current = self.head

        while current:
            blocks.append({
                "size": current.size,
                "process": current.process
            })
            current = current.next

        return blocks


memory = MemoryManager(TOTAL_MEMORY)


@app.route("/", methods=["GET", "POST"])
def index():
    global message, success

    if request.method == "POST":
        action = request.form.get("action")
        process = request.form.get("process", "").strip()

        if action == "reset":
            memory.__init__(TOTAL_MEMORY)
            history.clear()
            message = "Memory reset successfully."
            success = True
            return redirect(url_for("index"))

        if not process:
            message = "Please enter a process name."
            success = False
            return redirect(url_for("index"))

        blocks = memory.get_blocks()

        if action == "allocate":
            try:
                size = int(request.form.get("size", ""))
                if size <= 0:
                    raise ValueError
            except ValueError:
                message = "Enter a valid positive memory size."
                success = False
                return redirect(url_for("index"))

            if any(b["process"] == process for b in blocks):
                ok, remaining = False, 0
                message = f"NO: {process} is already allocated."
            else:
                ok, remaining = memory.allocate(process, size)

                if ok:
                    message = (
                        f"YES: {process} allocated {size} KB. "
                        f"{remaining} KB remains in the split block."
                    )
                else:
                    message = f"NO: Memory not available for {process}."

            success = ok
            history.insert(0, {
                "process": process,
                "operation": "Allocate",
                "size": size,
                "status": "YES" if ok else "NO"
            })

        elif action == "deallocate":
            ok, released = memory.deallocate(process)

            if ok:
                message = f"YES: {process} released {released} KB."
            else:
                message = f"NO: Process {process} not found."

            success = ok
            history.insert(0, {
                "process": process,
                "operation": "Deallocate",
                "size": released,
                "status": "YES" if ok else "NO"
            })

        return redirect(url_for("index"))

    blocks = memory.get_blocks()
    used = sum(
        b["size"] for b in blocks if b["process"] is not None
    )
    free = TOTAL_MEMORY - used

    return render_template(
        "index.html",
        blocks=blocks,
        history=history,
        total=TOTAL_MEMORY,
        used=used,
        free=free,
        count=sum(1 for b in blocks if b["process"] is not None),
        message=message,
        success=success,
        percent=used / TOTAL_MEMORY * 100
    )


import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )