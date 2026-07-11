import json
import codecs

with codecs.open('C:/Users/iamln/.gemini/antigravity-ide/brain/42eeb5d8-839b-4b91-a189-12a1d00a6d1b/.system_generated/logs/transcript_full.jsonl', 'r', 'utf-8') as f:
    i = 0
    for line in f:
        if 'TargetFile' in line and 'di.py' in line:
            obj = json.loads(line)
            tool_calls = obj.get('tool_calls', [])
            for call in tool_calls:
                args = call.get('arguments', {})
                if 'ReplacementContent' in args:
                    with codecs.open(f'chunk_{i}.py', 'w', 'utf-8') as out:
                        out.write(args['ReplacementContent'])
                    print(f'Wrote chunk_{i}.py')
                    i += 1
                elif 'ReplacementChunks' in args:
                    for chunk in args['ReplacementChunks']:
                        with codecs.open(f'chunk_{i}.py', 'w', 'utf-8') as out:
                            out.write(chunk['ReplacementContent'])
                        print(f'Wrote chunk_{i}.py')
                        i += 1
                elif 'CodeContent' in args:
                    with codecs.open(f'chunk_{i}.py', 'w', 'utf-8') as out:
                        out.write(args['CodeContent'])
                    print(f'Wrote chunk_{i}.py')
                    i += 1
