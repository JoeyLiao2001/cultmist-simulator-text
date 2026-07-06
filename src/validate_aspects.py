"""校验 OC 星座中每个物品的性相是否与数据集同类物品一致。"""
import json, sys
from collections import Counter

# 强制类别性相：该类型物品在游戏数据中 100% 携带的性相
MANDATORY = {
    '书籍': ['文献'],
    '工具': ['工具'],
    '原料': ['原料'],
    '地点': ['地点'],
    '密传': ['密传'],
    '影响': ['影响'],
    '召唤物': ['召唤物'],
    '回忆': ['回忆'],
    '伤疤': ['伤疤'],
    '诱惑': ['欲望'],
    '仪式': [],
    '传闻': [],
    '其他角色提及': [],
    '画作': ['工具'],       # 画作在游戏中归 tools
    '奇物': [],
    '珍品': [],
    '纪念物': [],
    '覆画残迹': [],
    '时节': [],
    '教团': [],
    '梦境': [],
    '藏宝地': ['地点'],
    '对手': [],
    '文章': ['文章'],
    '残骸': ['召唤物'],
}

def validate(oc_name, items):
    """items: list of dicts with keys: name, type, aspects"""
    errors = []
    for item in items:
        item_type = item['type']
        current = set(item.get('aspects', []))
        required = set(MANDATORY.get(item_type, []))
        missing = required - current
        if missing:
            errors.append(f"[{item_type}] {item['name']}: 缺少强制性相 {', '.join(sorted(missing))}")

    if errors:
        print(f'\n=== {oc_name} 性相校验 ===')
        for e in errors:
            print(f'  [MISS] {e}')
        print(f'  共 {len(errors)} 项缺失')
        return False
    else:
        print(f'\n=== {oc_name} 性相校验 ===')
        print(f'  [OK] 全部通过')
        return True

if __name__ == '__main__':
    # Example: validate Frizzelif
    frizzelif = [
        {'name':'烧焦的节目单','type':'工具','aspects':['工具','蛾']},
        {'name':'《翼中之翼》总谱残本','type':'书籍','aspects':['文献','蛾']},
        {'name':'咏叹调间的空白','type':'回忆','aspects':['蛾','回忆']},
        {'name':'被偷换的戒指','type':'原料','aspects':['启','原料']},
        {'name':'七排三座','type':'地点','aspects':['蛾','地点']},
        {'name':'《栖鸣录》','type':'密传','aspects':['蛾','密传']},
        {'name':'《教令》抄本','type':'书籍','aspects':['文献','心']},
        {'name':'河畔剧院的爪痕','type':'伤疤','aspects':['蛾','伤疤']},
        {'name':'林间的悸动','type':'诱惑','aspects':['蛾','欲望']},
        {'name':'拾滩鸦的一句话','type':'其他角色提及','aspects':[]},
    ]
    validate('喜鹊·夫里泽里夫', frizzelif)

    # Example: validate Anya
    anya = [
        {'name':'《无名日记》','type':'书籍','aspects':['文献','冬','秘史']},
        {'name':'哭丧人的披肩','type':'工具','aspects':['工具','冬']},
        {'name':'沃洛格达郊外的空坟','type':'地点','aspects':['冬']},
        {'name':'记名亡者','type':'召唤物','aspects':['冬','启']},
        {'name':'哑歌之仪','type':'仪式','aspects':['仪式','冬','启']},
        {'name':'预忘','type':'影响','aspects':['影响','冬','蛾']},
        {'name':'打听不得的女人','type':'传闻','aspects':['传闻','秘史','冬']},
        {'name':'维奥莱特的速写','type':'回忆','aspects':['冬','蛾']},
    ]
    validate('阿妮亚·沃洛格达', anya)
