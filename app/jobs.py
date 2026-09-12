import subprocess


class Jobs:
    def __init__(self):
        self.process_list = []

    def run_job(self, args: list[str]) -> None:
        process = subprocess.Popen(args)
        self.process_list.append((process, args + ["&"]))
        print(f"[{len(self.process_list)}] {process.pid}")

    def list_jobs(self) -> None:
        output = ""
        keep_items = []

        if len(self.process_list) == 0:
            return

        for i, item in enumerate(self.process_list):
            if i > 0:
                output += "\n"
            (process, args) = item
            status = "Done" if process.poll() is not None else "Running"
            if status == "Running":
                keep_items.append(item)
            sign = ""
            if len(self.process_list) - 1 == i:
                sign = "+"
            elif len(self.process_list) - 2 == i:
                sign = "-"
            output += (
                "["
                + str(i + 1)
                + "]"
                + self._add_empty_space_until(sign, 4)
                + self._add_empty_space_until(status, 24)
                + " ".join(args)
            )
        print(output)
        self.process_list = keep_items

    def _add_empty_space_until(self, text, until):
        while len(text) < until:
            text += " "
        return text
