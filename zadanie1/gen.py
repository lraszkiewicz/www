import os
import sys
import xlrd
import locale
import shutil

from slugify import slugify
from collections import defaultdict
from jinja2 import Template

locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')

results_dir = './results'  # for election results
out_dir = './out'  # for HTML output

# generated by get_voievodeships.py
voievodeship_of_district = {
    1: 'dolnośląskie', 2: 'dolnośląskie', 3: 'dolnośląskie', 4: 'dolnośląskie', 5: 'kujawsko-pomorskie',
    6: 'kujawsko-pomorskie', 7: 'kujawsko-pomorskie', 8: 'lubelskie', 9: 'lubelskie', 10: 'lubelskie', 11: 'lubelskie',
    12: 'lubelskie', 13: 'lubuskie', 14: 'lubuskie', 15: 'łódzkie', 16: 'łódzkie', 17: 'łódzkie', 18: 'łódzkie',
    19: 'łódzkie', 20: 'małopolskie', 21: 'małopolskie', 22: 'małopolskie', 23: 'małopolskie', 24: 'małopolskie',
    25: 'małopolskie', 26: 'małopolskie', 27: 'małopolskie', 28: 'mazowieckie', 29: 'mazowieckie', 30: 'mazowieckie',
    31: 'mazowieckie', 32: 'mazowieckie', 33: 'mazowieckie', 34: 'mazowieckie', 35: 'mazowieckie', 36: 'mazowieckie',
    37: 'opolskie', 38: 'opolskie', 39: 'podkarpackie', 40: 'podkarpackie', 41: 'podkarpackie', 42: 'podkarpackie',
    43: 'podlaskie', 44: 'podlaskie', 45: 'podlaskie', 46: 'pomorskie', 47: 'pomorskie', 48: 'pomorskie', 49: 'śląskie',
    50: 'śląskie', 51: 'śląskie', 52: 'śląskie', 53: 'śląskie', 54: 'śląskie', 55: 'świętokrzyskie',
    56: 'świętokrzyskie', 57: 'warmińsko-mazurskie', 58: 'warmińsko-mazurskie', 59: 'warmińsko-mazurskie',
    60: 'wielkopolskie', 61: 'wielkopolskie', 62: 'wielkopolskie', 63: 'wielkopolskie', 64: 'wielkopolskie',
    65: 'zachodniopomorskie', 66: 'zachodniopomorskie', 67: 'zachodniopomorskie', 68: 'zachodniopomorskie'
}

voievodeships = defaultdict(set)  # województwa
districts = defaultdict(set)  # okręgi wyborcze
municipalities = {}  # gminy

candidates = []
stats = []

if os.path.isdir(results_dir):
    for f in os.listdir(results_dir):
        if f.startswith('obw') and f.endswith('.xls'):
            sheet = xlrd.open_workbook(os.path.join(results_dir, f)).sheet_by_index(0)
            headers = [cell.value.replace('\n', ' ') for cell in sheet.row(0)]
            if not candidates:
                candidates = headers[headers.index('Głosy ważne') + 1:]
            if not stats:
                stats = headers[headers.index('Uprawnieni'):headers.index('Głosy ważne')+1]
            for row in list(sheet.get_rows())[1:]:
                row = [cell.value for cell in row]
                for i in range(headers.index('Uprawnieni'), len(headers)):
                    row[i] = int(row[i])
                row = dict(zip(headers, row))
                row['Nr okr.'] = int(row['Nr okr.'])
                row['Nr obw.'] = int(row['Nr obw.'])
                voievodeships[voievodeship_of_district[row['Nr okr.']]].add(row['Nr okr.'])
                districts[row['Nr okr.']].add((row['Kod gminy'], row['Gmina']))
                if not row['Kod gminy'] in municipalities:
                    municipalities[row['Kod gminy']] = (row['Gmina'], [])
                municipalities[row['Kod gminy']][1].append(row)
else:
    print('Directory {} does not exist.'.format(results_dir))
    sys.exit(0)

if os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir)

with open('./templates/results.html') as f:
    template = Template(f.read())

for v in voievodeships:
    print(v)
    v_dir = os.path.join(out_dir, slugify(v))
    v_results = defaultdict(int)
    v_children = []
    os.makedirs(v_dir)
    for d in sorted(voievodeships[v]):
        d_dir = os.path.join(v_dir, slugify('Okręg {}'.format(d)))
        d_results = defaultdict(int)
        d_children = []
        os.makedirs(d_dir)
        for m_id, m_name in districts[d]:
            m_dir = os.path.join(d_dir, slugify('{} {}'.format(m_name, m_id)))
            m_results = defaultdict(int)
            os.makedirs(m_dir)
            for row in municipalities[m_id][1]:
                for x in stats + candidates:
                    m_results[x] += row[x]
                    d_results[x] += row[x]
                    v_results[x] += row[x]
            m_results['Gmina'] = m_name
            m_results['slug'] = slugify('{} {}'.format(m_name, m_id))
            d_children.append(m_results)
            with open(os.path.join(m_dir, 'index.html'), 'w') as fm:
                fm.write(template.render(
                    breadcrumb=[('../../../', 'Polska'), ('../../', v), ('../', 'Okręg nr {}'.format(d))],
                    title=m_name,
                    headers=['Nr obw.', 'Adres'] + stats + candidates,
                    children=sorted(municipalities[m_id][1], key=lambda k: k['Nr obw.']),
                    results=m_results,
                    stats=stats,
                    candidates=candidates,
                    children_name='obwodach',
                    type='gminie'
                ))
        with open(os.path.join(d_dir, 'index.html'), 'w') as fd:
            fd.write(template.render(
                breadcrumb=[('../../', 'Polska'), ('../', v)],
                title='Okręg nr {}'.format(d),
                headers=['Gmina'] + stats + candidates,
                children=sorted(d_children, key=lambda k: locale.strxfrm(k['Gmina'])),
                link='Gmina'
            ))
        d_results['Nr okr.'] = d
        d_results['slug'] = slugify('Okręg {}'.format(d))
        v_children.append(d_results)
    with open(os.path.join(v_dir, 'index.html'), 'w') as fv:
        fv.write(template.render(
            breadcrumb=[('../', 'Polska')],
            title='{}'.format(v),
            headers=['Nr okr.'] + stats + candidates,
            children=sorted(v_children, key=lambda k: k['Nr okr.']),
            link='Nr okr.'
        ))
