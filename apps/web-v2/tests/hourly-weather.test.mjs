import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {ARCHIVE_SHA256, ORIGINAL_RESPONSE_SHA256, HOURLY_FIELDS, inspectHourlyArtifact, displayHourlyCell, taipeiTime} from '../hourly-weather.mjs';

const raw=await readFile(fileURLToPath(new URL('../fixtures/hourly/qixingtan-one-shot-20261019.json',import.meta.url)));
const archive=JSON.parse(raw);
const copy=()=>structuredClone(archive);

test('fixed offline one-shot remains historical and non-evaluable with 72 × 10 actual cells',()=>{
  assert.equal(createHash('sha256').update(raw).digest('hex'),ARCHIVE_SHA256);
  assert.equal(archive.source.source_sha256,ORIGINAL_RESPONSE_SHA256);
  assert.equal(archive.hours.length,72);
  assert.equal(archive.hours.reduce((sum,row)=>sum+Object.keys(row.values).length,0),720);
  const result=inspectHourlyArtifact(archive,Date.parse('2026-10-20T12:00:00Z'));
  assert.equal(result.state,'STALE');assert.equal(result.evaluation,'NOT_EVALUABLE');
  assert.equal(result.partial,false);
  assert.equal(result.source.provider_issued_at_utc,null);
  assert.equal(result.source.source_update_time_utc,null);
  assert.equal(taipeiTime(archive.hours[0].valid_at_utc,'en',{year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',hourCycle:'h23'}),'10/20/2026, 00');
});

test('W4 display fixture equals the accepted W5 zero-network replay artifact',async()=>{
  const replayBytes=await readFile(fileURLToPath(new URL('../../../ops/v2/evidence/open-meteo-one-shot-20261019/replay.json.gz',import.meta.url)));
  const replay=JSON.parse(gunzipSync(replayBytes));
  assert.equal(replay.operation,'OFFLINE_REPLAY');
  assert.equal(replay.network_attempts,0);
  assert.equal(replay.new_live_capture,false);
  assert.deepEqual(archive,replay.result.artifact);
});

test('missing, null and invalid cells are unavailable while a genuine zero remains zero',()=>{
  const item=copy();
  const zero=item.hours[0].values.cloud_cover_high;
  assert.equal(zero.value,0);assert.equal(displayHourlyCell(zero,'en'),'0 %');
  item.hours[0].values.cloud_cover_high={value:null,unit:'%',source_unit:'%',state:'UNAVAILABLE',reason_code:'NULL_VALUE'};
  item.availability='PARTIAL';
  const result=inspectHourlyArtifact(item,Date.parse('2026-10-20T12:00:00Z'));
  assert.equal(result.partial,true);assert.equal(displayHourlyCell(item.hours[0].values.cloud_cover_high,'en'),null);
  for(const bad of [false,'0',NaN,Infinity]){
    const changed=copy();changed.hours[0].values.cloud_cover_high.value=bad;
    assert.throws(()=>inspectHourlyArtifact(changed,Date.parse('2026-10-20T12:00:00Z')));
  }
});

test('pilot identity, unsafe evaluation metadata, time axis, units and clocks fail closed',()=>{
  const changes=[
    item=>item.place_id='tw-026', item=>item.recommendation_eligible=true,
    item=>item.photography_verdict='FAVORABLE', item=>item.source.provider_issued_at_utc='2026-10-19T16:00:00Z',
    item=>item.hours[1].valid_at_utc=item.hours[0].valid_at_utc,
    item=>item.hours[0].preceding_hour.start_utc=item.hours[0].valid_at_utc,
    item=>item.hours[0].values.temperature_2m.unit='°F',
    item=>item.source.source_sha256='0'.repeat(64)
  ];
  for(const change of changes){const item=copy();change(item);assert.throws(()=>inspectHourlyArtifact(item,Date.parse('2026-10-20T12:00:00Z')));}
  assert.throws(()=>inspectHourlyArtifact(archive,Date.parse('2026-10-19T15:00:00Z')));
  assert.equal(HOURLY_FIELDS.length,10);
});
