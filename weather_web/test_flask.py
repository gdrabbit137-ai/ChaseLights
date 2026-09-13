"""Test Flask route directly"""
from flask import Flask, jsonify, request
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from app import app

with app.test_client() as c:
    resp = c.get('/api/best-spots?region=tw')
    print('Status:', resp.status_code)
    if resp.status_code == 200:
        data = resp.get_json()
        print('Today:', len(data.get('today', [])), 'spots')
        for s in data['today'][:5]:
            print(f"  {s['name']}: {s['today']['score']} - {s['today'].get('best_genre','')}")
    else:
        import traceback, io
        tb = io.StringIO()
        traceback.print_exc(file=tb)
        print('Error body:', resp.data[:2000].decode('utf-8', errors='replace'))
    print('Done!')