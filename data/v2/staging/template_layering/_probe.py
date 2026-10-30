
import sys, json, glob
sys.path.insert(0,"D:/Dick/Project/ChaseLights/specs/v2/tests")
import importlib.util
spec=importlib.util.spec_from_file_location("vtw","D:/Dick/Project/ChaseLights/specs/v2/tests/validate_task_w_contracts.py")
vtw=importlib.util.module_from_spec(spec); spec.loader.exec_module(vtw)
bad=0
for p in sorted(glob.glob("D:/Dick/Project/ChaseLights/data/v2/opportunities/*.json")):
    d=json.loads(open(p,encoding="utf-8").read())
    e=vtw.validate_record(d)
    if e: bad+=1; print(p,e[:2])
print("offenders:",bad)
