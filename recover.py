import json
import os


def apply_replace(target_file, target_content, replacement_content):
    if not os.path.exists(target_file):
        print(f"File {target_file} does not exist for replace")
        return
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
    if target_content in content:
        content = content.replace(target_content, replacement_content)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Applied replace to {target_file}")
    else:
        print(f"Target content not found in {target_file}")


def recover():
    # 1. Restore tracked files
    os.system("git restore app/")
    os.system("git restore tests/")

    transcript_path = r"C:\Users\Sri Balagi\.gemini\antigravity-ide\brain\13a6893f-cb4a-49c9-9258-f677800b0a8a\.system_generated\logs\transcript_full.jsonl"

    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            step = json.loads(line)
            if "tool_calls" in step:
                for call in step["tool_calls"]:
                    name = call.get("name")
                    args = call.get("args", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except:
                            continue

                    if name == "write_to_file":
                        target = args.get("TargetFile")
                        content = args.get("CodeContent")
                        if target and content and "recover.py" not in target:
                            os.makedirs(os.path.dirname(target), exist_ok=True)
                            with open(target, "w", encoding="utf-8") as out:
                                out.write(content)
                            print(f"Recovered {target} via write_to_file")

                    elif name == "multi_replace_file_content":
                        target = args.get("TargetFile")
                        chunks = args.get("ReplacementChunks", [])
                        if "recover.py" in target:
                            continue
                        for chunk in chunks:
                            apply_replace(
                                target,
                                chunk.get("TargetContent"),
                                chunk.get("ReplacementContent"),
                            )

                    elif name == "replace_file_content":
                        target = args.get("TargetFile")
                        if "recover.py" in target:
                            continue
                        apply_replace(
                            target,
                            args.get("TargetContent"),
                            args.get("ReplacementContent"),
                        )


if __name__ == "__main__":
    recover()
