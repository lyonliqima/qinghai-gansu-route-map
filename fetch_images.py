#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search Wikimedia Commons for open-licensed photos of each route point and download them."""
import json, os, re, sys, time, urllib.parse, urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
os.makedirs(OUT, exist_ok=True)
UA = 'QinghaiGansuTripMap/1.0 (personal travel map; contact: local)'

QUERIES = {
    '莫高窟': ['Mogao Caves', 'Mogao Grottoes', '莫高窟'],
    '琉璃湖（奶子湖）': ['Naiter Lake Qinghai', '奶子湖'],
    '大柴旦翡翠湖': ['Da Qaidam Emerald Lake', 'Emerald Lake Qinghai', '翡翠湖 大柴旦'],
    '阿克塞石油小镇': ['Aksai Kazakhstan Autonomous County', '阿克塞', 'Bolotuojing'],
    '大地之子·无界': ['Son of the Earth sculpture Gansu', '大地之子 雕塑 瓜州'],
    '榆林窟': ['Yulin Caves', 'Yulin Grottoes', '榆林窟'],
    '悬壁长城': ['Overhanging Great Wall Jiayuguan', '悬壁长城'],
    '新城魏晋墓画廊': ['Wei Jin tomb murals Jiayuguan', '新城魏晋墓'],
    '西宁曹家堡机场': ['Xining Caojiabao International Airport'],
    '德令哈（住全季）': ['Delingha', '德令哈'],
    '冷湖镇 · 美豪酒店': ['Lenghu', '冷湖'],
    '敦煌 · 柏柏里民宿': ['Dunhuang Mingsha Mountain', '鸣沙山 敦煌'],
    '瓜州（住）': ['Guazhou County Gansu', '瓜州 甘肃'],
    '嘉峪关（住）': ['Jiayuguan Gansu cityscape', 'Jiayuguan railway station', '嘉峪关市'],
    '海西州民族博物馆': ['Haixi Prefecture Museum', 'Delingha museum', '德令哈 博物馆'],
    '敦煌博物馆': ['Dunhuang Museum', '敦煌博物馆'],
    '嘉峪关长城博物馆': ['Great Wall Museum Jiayuguan', '嘉峪关长城博物馆'],
    '嘉峪关城市博物馆': ['Jiayuguan City Museum Gansu', '嘉峪关市 城市博物馆', 'Jiuquan steel industry'],
    '海子诗歌陈列馆': ['Delingha Hai Zi poetry', '海子诗歌陈列馆'],
    '甘肃简牍博物馆（兰州）': ['Gansu Museum bamboo slips', '甘肃简牍博物馆'],
    '茶卡盐湖': ['Chaka Salt Lake', '茶卡盐湖'],
    '金子海': ['Jinzihai', '金子海'],
    '德令哈光热电站': ['solar power tower China', 'solar thermal power plant heliostats'],
    '柏树山': ['Qilian juniper forest', '柏树山 德令哈'],
    '可鲁克湖': ['Keluke Lake', '可鲁克湖'],
    '托素湖·外星人遗址': ['Tuosu Lake', '托素湖'],
    '小柴旦湖': ['Xiao Qaidam Lake', '小柴旦湖'],
    '大柴旦红崖火星基地': ['Mars simulation base China desert', '红崖 火星'],
    'G315 U 型公路': ['China National Highway 315', 'G315 公路'],
    '冷湖石油基地遗址': ['Lenghu oil base ruins', '冷湖石油'],
    '黑独山': ['black gravel mountain Qinghai desert', '黑独山 冷湖', 'Lenghu yardang'],
    '赛什腾山天文台址': ['Lenghu observatory', 'astronomical observatory Qinghai', '赛什腾山 天文台'],
    '苏干湖': ['Sugan Lake', '苏干湖'],
    '多坝沟胡杨峡': ['Populus euphratica forest Gansu', '胡杨林 甘肃'],
    '敦煌光热电站（超级镜子发电站）': ['Dunhuang solar thermal power station', 'molten salt tower solar plant China', '敦煌 光热电站'],
    '西千佛洞': ['Western Thousand Buddha Caves', '西千佛洞'],
    '敦煌雅丹魔鬼城': ['Dunhuang Yardang National Geopark', 'yardang Gansu', '雅丹地貌'],
    '玉门关·汉长城': ['Yumen Pass', '玉门关'],
    '阳关': ['Yangguan', '阳关'],
    '鸣沙山·月牙泉': ['Mingsha Mountain', 'Crescent Lake Dunhuang', '鸣沙山 月牙泉'],
    '锁阳城遗址': ['Suoyangcheng', '锁阳城'],
    '汉武雄风雕塑': ['Han Wudi statue Gansu desert', '汉武雄风'],
    '长城第一墩': ['Great Wall first pier Jiayuguan', '长城第一墩'],
    '嘉峪关关城': ['Jiayuguan Pass', 'Jiayuguan Fort', '嘉峪关关城'],
    '黑山岩画': ['petroglyphs Gansu Heishan', '黑山岩画'],
    '紫轩葡萄酒庄园': ['vineyard Hexi Corridor Gansu', '紫轩葡萄酒'],
    '方特丝路神画': ['Fantawild Silk Road Dreamland', '方特 丝路神画'],
    '俄博梁·火星营地': ['Eboliang yardang', '火星营地 冷湖', 'Qaidam Basin yardang', 'Mars camp desert China'],
    '洪水河大峡谷（备选）': ['Hongshuihe canyon', '洪水河大峡谷', 'Jiuquan waterfall Qilian', 'canyon Gansu Qilian mountains'],
}


def api(params):
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    delay = 2.0
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            code = getattr(e, 'code', None)
            if attempt == 4:
                raise
            print('   retry(%d) %s' % (attempt + 1, code or e))
            time.sleep(delay)
            delay *= 2
    return {}


def search(query, limit=6):
    try:
        data = api({
            'action': 'query', 'format': 'json', 'generator': 'search',
            'gsrsearch': 'filetype:bitmap ' + query, 'gsrnamespace': '6',
            'gsrlimit': str(limit), 'prop': 'imageinfo',
            'iiprop': 'url|mime|size|extmetadata', 'iiurlwidth': '720',
        })
    except Exception as e:
        print('   search error:', e)
        return []
    pages = (data.get('query') or {}).get('pages') or {}
    out = []
    for p in pages.values():
        ii = (p.get('imageinfo') or [None])[0]
        if not ii:
            continue
        if ii.get('mime') not in ('image/jpeg', 'image/png'):
            continue
        thumb = ii.get('thumburl') or ii.get('url')
        if not thumb:
            continue
        lic = ((ii.get('extmetadata') or {}).get('LicenseShortName') or {}).get('value', '')
        out.append({'title': p.get('title'), 'thumb': thumb, 'w': ii.get('width'), 'h': ii.get('height'),
                    'license': lic, 'descurl': ii.get('descriptionurl')})
    return out


def slug(name, idx):
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '_', name).strip('_')
    return '%02d_%s.jpg' % (idx, s)


def download(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
    if len(data) < 4000:
        return False
    with open(dest, 'wb') as f:
        f.write(data)
    return True


def main():
    mapf = os.path.join(os.path.dirname(OUT), 'image_map.json')
    result = {}
    if os.path.exists(mapf):
        try:
            prev = json.load(open(mapf))
            result = {k: v for k, v in prev.items()
                      if os.path.exists(os.path.join(os.path.dirname(OUT), v['file']))}
        except Exception:
            result = {}
    idx = 0
    for name, queries in QUERIES.items():
        idx += 1
        if name in result:
            print('SKIP  %s' % name)
            continue
        got = None
        for q in queries:
            hits = search(q)
            if hits:
                got = hits[0]
                break
            time.sleep(1.2)
        if not got:
            print('MISS  %s' % name)
            continue
        fn = slug(name, idx)
        dest = os.path.join(OUT, fn)
        try:
            if download(got['thumb'], dest):
                result[name] = {'file': 'img/' + fn, 'title': got['title'], 'license': got['license'],
                                'src': got['descurl']}
                print('OK    %-28s %-40s [%s]' % (name, got['title'][5:60], got['license']))
            else:
                print('SMALL %s' % name)
        except Exception as e:
            print('DLERR %s %s' % (name, e))
        time.sleep(0.2)
    with open(os.path.join(os.path.dirname(OUT), 'image_map.json'), 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print('\n--- got %d / %d ---' % (len(result), len(QUERIES)))


if __name__ == '__main__':
    main()
