import UnityPy, os

game = 'D:/SteamLibrary/steamapps/common/Cultist Simulator/cultistsimulator_Data'
out_dir = 'output/assets/icons'
os.makedirs(out_dir, exist_ok=True)

# Find principle icons by exact sprite name
targets = ['winter', 'knock', 'edge', 'forge', 'grail', 'heart', 'lantern', 'moth', 'secret', 'secrethistories']

extracted = 0
for fname in sorted(os.listdir(game)):
    if not fname.endswith('.assets'):
        continue
    path = os.path.join(game, fname)
    try:
        env = UnityPy.load(path)
        for obj in env.objects:
            if obj.type.name == 'Sprite':
                data = obj.read()
                name = str(data.m_Name).lower().strip()
                # Match principle icons - look for exact name or common icon naming
                for t in targets:
                    if name == t or name == f'aspect_{t}' or name == f'aspect.{t}' or name == f'{t}_icon' or name == f'icon_{t}':
                        try:
                            img = data.image
                            safe_name = data.m_Name
                            img.save(os.path.join(out_dir, f'{safe_name}.png'))
                            print(f'EXTRACTED: {fname} -> {safe_name}.png')
                            extracted += 1
                        except Exception as e:
                            print(f'Save failed for {data.m_Name}: {e}')
    except Exception as e:
        pass

# Also dump all names containing winter or knock to see the naming pattern
print('\n--- All winter/knock sprites ---')
for fname in sorted(os.listdir(game)):
    if not fname.endswith('.assets'):
        continue
    path = os.path.join(game, fname)
    try:
        env = UnityPy.load(path)
        for obj in env.objects:
            if obj.type.name == 'Sprite':
                data = obj.read()
                name = str(data.m_Name)
                nl = name.lower()
                if 'winter' in nl or 'knock' in nl:
                    print(f'{name}')
    except:
        pass

print(f'\nExtracted: {extracted}')
