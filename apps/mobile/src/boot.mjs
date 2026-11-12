// Boot orchestrator: version check -> (new? background download) -> offline degrade.
// Thin glue so the WebView can call it from index bootstrap; logic lives in
// version-check.mjs / i18n/index.mjs and is unit-tested directly.
import {createVersionChecker} from './version-check.mjs';
import {createI18n} from './i18n/index.mjs';

export async function boot({checker, i18n, push, onStatus = () => {}} = {}) {
  if (!checker || !i18n) throw new Error('boot: checker and i18n are required');
  const result = await checker.check();
  const messageKey = {
    current: 'dataCurrent',
    new: 'dataNew',
    first: 'firstRun',
    offline: 'offlineUsingCache',
    'offline-no-cache': 'offlineNoCache'
  }[result.status] ?? 'loadError';
  onStatus({phase: 'checked', status: result.status, message: i18n.t(messageKey)});
  if (result.status === 'new' || result.status === 'first') {
    // Fire-and-forget background refresh; UI keeps serving cached data meanwhile.
    checker.download(result.remoteDigest)
      .then((r) => onStatus({phase: 'downloaded', status: r.status,
        message: i18n.t(r.status === 'cached' ? 'dataUpdated' : 'digestMismatch')}))
      .catch(() => onStatus({phase: 'downloaded', status: 'download-failed',
        message: i18n.t('loadError')}));
  }
  // CL-APP-03: APP push base — fire-and-forget; a push failure never breaks
  // boot (the registrar degrades gracefully when FCM is unavailable).
  if (push) {
    Promise.resolve(push.start()).catch((e) => console.info(`[push] startup skipped: ${e && e.message}`));
  }
  return result;
}

export {createVersionChecker, createI18n};
export {createPushRegistrar, defaultPushPlugin, registerPushToken, PUSH_CHANNEL_ID} from './push.mjs';
