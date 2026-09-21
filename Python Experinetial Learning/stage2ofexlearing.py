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

                # Split the block if extra memory is available
                if current.size > size:
                    new_block = MemoryBlock(current.size - size)
                    new_block.next = current.next
                    current.next = new_block

                current.size = size
                current.process = process

                print(process, "allocated", size, "KB")
                return True

            current = current.next

        print("Memory not available for", process)
        return False

    def deallocate(self, process):
        current = self.head

        while current:
            if current.process == process:
                current.process = None
                print(process, "memory released")
                return

            current = current.next

        print("Process not found")

    def display(self):
        current = self.head

        print("\nMemory Status:")
        while current:
            if current.process is None:
                print("[ FREE :", current.size, "KB ]")
            else:
                print("[", current.process, ":", current.size, "KB ]")

            current = current.next


# Main Program
memory = MemoryManager(1000)

memory.allocate("P1", 200)
memory.allocate("P2", 300)
memory.allocate("P3", 150)

memory.display()

memory.deallocate("P2")

memory.display()

memory.allocate("P4", 250)

memory.display()