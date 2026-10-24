"""V1.1 deterministic helpers. Image interpretation belongs to Codex/human reviewers."""
import argparse
import json
from pathlib import Path
import re

VERSION = '1.1.0'
MODES = ('cmf_transfer', 'local_edit', 'scene_transfer', 'render_refinement', 'view_consistency_review', 'visual_qa')
CONF = ('Confirmed', 'Observed', 'Inferred', 'Unknown')
STATUSES = ('PASS', 'REVIEW', 'FAIL', 'NOT_TESTED')
DIMENSIONS = ('geometry', 'components', 'proportions', 'preserved_cmf', 'edit_boundary', 'output_spec', 'render_quality')

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def validate_dna(d):
    errors = []
    required = {'schema_version': str, 'product_id': str, 'product_name': str, 'source_assets': list,
                'geometry_features': list, 'components': list, 'cmf_features': list, 'visual_features': list,
                'design_locks': list, 'unknowns': list, 'revision': int}
    if not isinstance(d, dict):
        return ['DNA must be an object']
    for key, typ in required.items():
        if key not in d or type(d[key]) is not typ:
            errors.append('invalid field: ' + key)
    if errors:
        return errors
    if d['schema_version'] != '1.0' or d['revision'] < 1:
        errors.append('unsupported schema/revision')
    ids = set()
    for asset in d['source_assets']:
        if not isinstance(asset, dict) or not all(isinstance(asset.get(k), str) and asset[k] for k in ('id','path','role','source')):
            errors.append('invalid source asset')
        elif asset['id'] in ids:
            errors.append('duplicate asset id')
        else:
            ids.add(asset['id'])
    for group in ('geometry_features','components','cmf_features','visual_features'):
        for feature in d[group]:
            if not isinstance(feature, dict) or not all(k in feature for k in ('id','attribute','value','source','confidence')):
                errors.append('invalid feature: ' + group)
                continue
            if feature['confidence'] not in CONF or not isinstance(feature['source'], list) or not set(feature['source']) <= ids:
                errors.append('invalid feature evidence')
            if feature['confidence'] == 'Unknown' and feature['value'] is not None:
                errors.append('Unknown must have null value')
    lock_ids = set()
    for lock in d['design_locks']:
        if not isinstance(lock, dict) or not all(k in lock for k in ('id','target','attribute','level','expected','allowed_change','source','confidence','severity')):
            errors.append('incomplete lock')
            continue
        if not all(isinstance(lock[k], str) and lock[k] for k in ('id','target','attribute','severity')):
            errors.append('invalid lock strings')
        if lock['id'] in lock_ids:
            errors.append('duplicate lock id')
        lock_ids.add(lock['id'])
        if lock['level'] not in ('Hard','Conditional','Editable') or lock['confidence'] not in CONF:
            errors.append('invalid lock enum')
        if lock['severity'] not in ('critical','major','minor'):
            errors.append('invalid severity')
        if not isinstance(lock['source'], list) or not set(lock['source']) <= ids or not lock['source']:
            errors.append('invalid lock evidence')
        if lock['level'] == 'Hard' and (lock['confidence'] not in ('Confirmed','Observed') or lock['allowed_change'] not in (None, '', 'none', '不允许')):
            errors.append('Hard lock conflicts with evidence or allowed change')
        if lock['confidence'] == 'Unknown' and lock['expected'] is not None:
            errors.append('Unknown lock must use null')
    return errors

def route(text):
    rules = [('visual_qa', ('审查','质检','qa')), ('view_consistency_review', ('后视','多视角','正视','侧视','俯视','三视图')),
             ('local_edit', ('局部','轮眉','充电口','增加','删除')), ('cmf_transfer', ('cmf','材质','颜色','配色')),
             ('scene_transfer', ('背景','场景')), ('render_refinement', ('高清','清晰','渲染','降噪'))]
    hits = [mode for mode, words in rules if any(word in text.lower() for word in words)]
    return hits[0] if hits else None

def validate_view_plan(plan, dna):
    """Validate declared view bindings, not CAD truth or image content."""
    if not isinstance(plan, dict):
        return ['view_plan must be an object']
    errors = []
    mode = plan.get('mode')
    if mode not in ('concept_reference','provided_views','cad_projection'):
        errors.append('invalid view_plan mode')
    if plan.get('accuracy') not in ('conceptual','source_constrained'):
        errors.append('invalid view_plan accuracy')
    if mode == 'concept_reference' and plan.get('accuracy') != 'conceptual':
        errors.append('single-image concept cannot claim source-constrained accuracy')
    if not isinstance(plan.get('unverified'), list):
        errors.append('view_plan requires unverified list')
    views = plan.get('views')
    if not isinstance(views, list) or len(views) != 3:
        return errors + ['three-view plan requires exactly three views']
    assets = {a['id']:a for a in dna['source_assets']}
    names, targets = [], []
    for view in views:
        if not isinstance(view, dict):
            errors.append('view must be an object')
            continue
        name, target = view.get('view'), view.get('target_asset')
        if name not in ('front','rear','left','right','top','bottom'):
            errors.append('invalid view direction')
        names.append(name)
        if not isinstance(target, str) or target not in assets:
            errors.append('view target_asset must reference an input asset')
        else:
            role = assets[target]['role']
            expected_roles = ('cad',) if mode == 'cad_projection' else ('target',)
            if role not in expected_roles:
                errors.append('view source role incompatible with mode')
            targets.append(target)
        if view.get('projection') not in ('orthographic','perspective','unknown'):
            errors.append('invalid projection')
        if mode == 'cad_projection' and view.get('projection') != 'orthographic':
            errors.append('CAD three-view output requires orthographic projection')
        if not isinstance(view.get('unverified'), list):
            errors.append('each view requires unverified list')
    if len(set(str(name) for name in names)) != len(names):
        errors.append('duplicate view directions')
    if mode == 'provided_views' and len(set(targets)) != 3:
        errors.append('provided views require three distinct target assets')
    return errors

def validate_brief(b, dna):
    errors = []
    if b.get('task_type') not in MODES:
        errors.append('task_type must be explicit or resolved')
    for field in ('objective','allowed_changes','output_requirements','uncertainty','manual_steps'):
        if field not in b:
            errors.append('missing brief field: ' + field)
    if not isinstance(b.get('allowed_changes'), list):
        errors.append('allowed_changes must be a list')
        return errors
    assets = {a['id']: a for a in dna['source_assets']}
    plan = b.get('view_plan')
    target_roles = ('target','cad') if isinstance(plan,dict) and plan.get('mode') == 'cad_projection' else ('target',)
    if b.get('target_asset') not in assets or assets.get(b.get('target_asset'), {}).get('role') not in target_roles:
        errors.append('target asset role incompatible with task')
    if not isinstance(b.get('reference_assets'), list) or not set(b.get('reference_assets', [])) <= set(assets):
        errors.append('invalid reference assets')
    for lock in dna['design_locks']:
        if any(change.get('target') == lock['target'] and change.get('attribute') == lock['attribute'] for change in b['allowed_changes']):
            if lock['level'] == 'Hard':
                errors.append('allowed change conflicts with Hard lock ' + lock['id'])
            if lock['level'] == 'Conditional' and not any(change.get('authorization') for change in b['allowed_changes'] if change.get('target') == lock['target'] and change.get('attribute') == lock['attribute']):
                errors.append('Conditional change requires authorization')
    if 'view_plan' in b:
        errors += validate_view_plan(b['view_plan'], dna)
    return errors

def prompt(dna, brief):
    assets = {a['id']: a for a in dna['source_assets']}
    sections = {
        'Target Image': assets[brief['target_asset']],
        'Reference Images': [assets[i] for i in brief['reference_assets']],
        'Edit Objective': brief['objective'],
        'Preserve': [l for l in dna['design_locks'] if l['level'] == 'Hard' or (l['level'] == 'Conditional' and not any(c.get('target') == l['target'] and c.get('attribute') == l['attribute'] and c.get('authorization') for c in brief['allowed_changes']))],
        'Allowed Changes': brief['allowed_changes'],
        'Forbidden Changes': ['禁止跨角色迁移造型；未授权属性保持原样；禁止补造不可见结构。'],
        'Output Requirements': ({'requirements':brief['output_requirements'], 'view_plan':brief['view_plan']} if 'view_plan' in brief else brief['output_requirements']),
        'Uncertainty': dna['unknowns'] + brief['uncertainty'],
    }
    return '\n\n'.join('## ' + key + '\n' + json.dumps(value, ensure_ascii=False, indent=2) for key, value in sections.items())

def assess(dna, result_path, findings):
    """Aggregate reviewer evidence; never infer visual facts from numbers or filenames."""
    if not result_path or not Path(result_path).is_file():
        return {'status':'NOT_TESTED', 'dimensions':{d:'NOT_TESTED' for d in DIMENSIONS}, 'findings':[], 'unverified':['缺少可读取结果图']}
    locks = {l['id']:l for l in dna['design_locks']}
    normalized = []
    dimensions = {d:'NOT_TESTED' for d in DIMENSIONS}
    for f in findings:
        if f.get('dimension') not in dimensions or f.get('status') not in STATUSES:
            raise ValueError('invalid QA finding')
        item = dict(f)
        if not f.get('evidence') or not f.get('reviewer'):
            item['status'] = 'NOT_TESTED'
        elif not f.get('reliable', False):
            item['status'] = 'REVIEW'
        elif f.get('violation') and locks.get(f.get('lock_id'), {}).get('level') == 'Hard':
            item['status'] = 'FAIL'
        normalized.append(item)
        old = dimensions[f['dimension']]
        rank = {'PASS':0,'NOT_TESTED':1,'REVIEW':2,'FAIL':3}
        dimensions[f['dimension']] = item['status'] if old == 'NOT_TESTED' else max((old,item['status']), key=rank.get)
    states = list(dimensions.values())
    status = 'FAIL' if 'FAIL' in states else 'REVIEW' if 'REVIEW' in states else 'NOT_TESTED' if 'NOT_TESTED' in states else 'PASS'
    return {'status':status, 'dimensions':dimensions, 'findings':normalized, 'unverified':[k for k,v in dimensions.items() if v == 'NOT_TESTED']}

def prepare(dna, brief, out):
    errors = validate_dna(dna)
    if not errors:
        errors += validate_brief(brief, dna)
    if errors:
        raise ValueError('; '.join(errors))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError('输出目录非空，请使用新的 case/revision 目录')
    def save(name, value):
        (out/name).write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    save('product-dna.json', dna)
    save('design-brief.md', '# 设计任务单\n\n```json\n'+json.dumps(brief,ensure_ascii=False,indent=2)+'\n```')
    save('edit-prompt.md', prompt(dna,brief))
    save('change-log.md', '# 修改记录\n\n已生成约束与提示词。未执行图像编辑；等待实际结果与人工视觉审查。')
    manifest = {'case_id':out.name,'skill_version':VERSION,'task_type':brief['task_type'], 'input_assets':dna['source_assets'],
                'tools_used':['Python standard library: prepare'], 'actual_image_edit':False,
                'files':['product-dna.json','design-brief.md','edit-prompt.md','change-log.md','run-manifest.json'],
                'qa_status':'NOT_TESTED','execution_status':'PROMPT_READY','unverified':dna['unknowns']+['真实图像编辑和视觉审查尚未执行']}
    if 'view_plan' in brief:
        manifest['view_plan'] = brief['view_plan']
        manifest['unverified'] += brief['view_plan']['unverified']
        for view in brief['view_plan']['views']:
            manifest['unverified'] += view['unverified']
    save('run-manifest.json',manifest)
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    v=sub.add_parser('validate'); v.add_argument('dna')
    r=sub.add_parser('route'); r.add_argument('request')
    c=sub.add_parser('capabilities')
    a=sub.add_parser('prepare'); a.add_argument('--dna',required=True); a.add_argument('--brief',required=True); a.add_argument('--out',required=True)
    q=sub.add_parser('qa'); q.add_argument('--dna',required=True); q.add_argument('--result',required=True); q.add_argument('--findings',required=True); q.add_argument('--out',required=True)
    args=p.parse_args()
    if args.command=='validate':
        errors=validate_dna(read(args.dna)); print(json.dumps(errors,ensure_ascii=False)); return bool(errors)
    if args.command=='route':
        print(json.dumps({'suggested_task':route(args.request),'note':'关键词仅建议；混合任务由 Codex 拆分并确认作用范围。'},ensure_ascii=False))
    if args.command=='capabilities':
        import importlib.util
        print(json.dumps({'file_operations':True,'tests':True,'local_image_processing':bool(importlib.util.find_spec('PIL')),
                          'image_analysis':'CHECK_SESSION','image_editor':'CHECK_SESSION','note':'Python 无法枚举 Codex 会话工具；不得据此推断已授权。'},ensure_ascii=False))
    if args.command=='prepare':
        print(json.dumps(prepare(read(args.dna),read(args.brief),args.out),ensure_ascii=False))
    if args.command=='qa':
        dna=read(args.dna)
        if validate_dna(dna): raise ValueError('invalid DNA')
        result=assess(dna,args.result,read(args.findings))
        output=Path(args.out)
        report='# Visual QA\n\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n\n修正要求：逐条修复 FAIL；REVIEW 补充视图或人工确认；未检查项不得视为通过。'
        with output.open('x',encoding='utf-8') as f: f.write(report)
        print(result['status'])
    return 0

if __name__=='__main__':
    raise SystemExit(main())
