// CL-APP-02: Capacitor shell entry cases — pull-to-refresh re-fetch trigger and
// the trilingual sign-in entry. The logic lives in apps/web-v2 (the WebView
// loads the deployed web-v2 page via server.url; www is the fallback bundle),
// and these tests exercise the same modules the shell page runs.
import {test} from "node:test";
import assert from "node:assert/strict";
import {createPullToRefresh, fetchCloudDigest} from "../../web-v2/pull-refresh.mjs";
import {AUTH_START_ENDPOINTS, AUTH_ME_ENDPOINT, parseMember, fetchMember} from "../../web-v2/shell-auth.mjs";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname, join} from "node:path";

const webV2 = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "web-v2");

function touch(y) { return {touches: [{clientY: y}]}; }

test("下拉：在頁頂往下拉超過門檻觸發重整手勢，頁中滑動不觸發", () => {
  let refreshes = 0;
  const pull = createPullToRefresh({threshold: 80, atTop: () => true, onRefresh: () => { refreshes++; }});
  pull.handleTouchStart(touch(200));
  pull.handleTouchMove(touch(285)); // 85px — over threshold
  pull.handleTouchEnd();
  assert.equal(refreshes, 1);
  const midPage = createPullToRefresh({threshold: 80, atTop: () => false, onRefresh: () => { refreshes++; }});
  midPage.handleTouchStart(touch(200));
  midPage.handleTouchMove(touch(500));
  midPage.handleTouchEnd();
  assert.equal(refreshes, 1); // unchanged
});

test("重整：重抓 bundle digest 端點（/api/v1/catalog/digests），離線時回 null 不拋錯", async () => {
  let probed = 0;
  const digest = await fetchCloudDigest((url) => {
    probed++;
    assert.equal(url, "/api/v1/catalog/digests");
    return {ok: true, json: async () => ({digest: "deadbeef"})};
  });
  assert.equal(probed, 1);
  assert.equal(digest, "deadbeef");
  assert.equal(await fetchCloudDigest(async () => { throw new Error("offline"); }), null);
});

test("登入入口：端點指向 LINE／Google OAuth start，錨點存在於 shell 頁面", () => {
  assert.equal(AUTH_START_ENDPOINTS.line, "/api/v1/auth/line/start");
  assert.equal(AUTH_START_ENDPOINTS.google, "/api/v1/auth/google/start");
  assert.equal(AUTH_ME_ENDPOINT, "/auth/me");
  const html = readFileSync(join(webV2, "index.html"), "utf8");
  assert.ok(html.includes(`href="${AUTH_START_ENDPOINTS.line}"`), "LINE start anchor");
  assert.ok(html.includes(`href="${AUTH_START_ENDPOINTS.google}"`), "Google start anchor");
});

test("登入入口：/auth/me 回應渲染會員名稱，未登入時顯示登入按鈕（fail closed）", async () => {
  const res = () => ({ok: true, json: async () => ({display_name: "小美"})});
  const member = parseMember(await res().json());
  assert.equal(member.name, "小美");
  const emptyRes = () => ({ok: true, json: async () => ({})});
  const none = parseMember(await emptyRes().json());
  assert.equal(none, null);
  assert.equal(parseMember({display_name: "  "}), null);
  assert.deepEqual(await fetchMember(async () => ({ok: false})), null);
});
